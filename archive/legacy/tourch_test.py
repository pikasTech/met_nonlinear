import torch
import torch.nn as nn
import torch.optim as optim
import math
import matplotlib.pyplot as plt

class SOSunit(nn.Module):
    def __init__(self):
        super(SOSunit, self).__init__()

    def freq_response(self, w: torch.Tensor, b0, b1, b2, a0, a1, a2, gate):
        """
        连续域二阶滤波器传递函数:
          H(s) = (b0 + b1 s + b2 s^2) / (a0 + a1 s + a2 s^2)
        在频域上 s = j * w
        """
        s = 1j * w
        numerator = b0 + b1*s + b2*(s**2)
        denominator = 1 + a1*s + a2*(s**2)
        H = numerator / denominator
        # return gate * H  # 如需要门控开关可保留，否则可直接 return H
        return H

class SOSConnect(nn.Module):
    """
    定义了并联(多个并联支路) + 串联(每个并联支路内多个串联的SOS)的结构。
    """
    def __init__(self, num_parallel, num_series):
        super(SOSConnect, self).__init__()
        self.num_parallel = num_parallel
        self.num_series = num_series
        # 创建 num_parallel 行，每行 num_series 个 SOS 单元
        self.layers = nn.ModuleList(
            [
                nn.ModuleList([SOSunit() for _ in range(num_series)]) 
                for _ in range(num_parallel)
            ]
        )
    
    def freq_response(self, w, params):
        """
        输入:
            w: 频率向量 (Tensor)
            params: 大小为 (total_sos, 7) 的参数Tensor，其中:
                    [b0, b1, b2, a0, a1, a2, gate]
        返回:
            total_response: 并联 + 串联 结构的总频响
        """
        total_response = torch.zeros_like(w, dtype=torch.complex64)
        idx = 0
        for row_units in self.layers:
            # 每行(并联支路)先串联相乘
            row_resp = torch.ones_like(w, dtype=torch.complex64)
            for _ in row_units:
                b0, b1, b2, a0, a1, a2, gate = params[idx]
                row_resp *= SOSunit().freq_response(w, b0, b1, b2, a0, a1, a2, gate)
                idx += 1
            # 并联支路之间相加
            total_response += row_resp
        return total_response

    def summary(self):
        print('SOSConnect Summary:')
        print(f'Number of parallel: {self.num_parallel}')
        print(f'Number of series: {self.num_series}')
        print(f'Total number of SOS units: {self.num_parallel * self.num_series}')

class ParamPredictorTransformer(nn.Module):
    """
    使用 Transformer Encoder 来预测滤波器系数。
    输入: x, shape = (batch_size, 2*freq_bins)
         其中 (H_target.real, H_target.imag) 拼到一起。
    输出: (batch_size, output_size) -> 即滤波器参数。
    """

    def __init__(
        self,
        freq_bins: int,
        output_size: int,
        embed_dim: int = 64,
        nhead: int = 4,
        num_layers: int = 2,
        dropout: float = 0.0
    ):
        """
        freq_bins: 频率点数量
        output_size: 需要预测的总参数维度 (total_sos * param_per_sos)
        embed_dim: 每个token(频率)的嵌入维度
        nhead: 多头注意力的头数
        num_layers: TransformerEncoder层数
        dropout: dropout概率
        """
        super().__init__()
        self.freq_bins = freq_bins
        self.embed_dim = embed_dim

        # 用线性层先把 2D(实部+虚部) embed 到 embed_dim
        self.input_embed = nn.Linear(2, embed_dim)

        # 可学习的位置编码(也可以换成正弦位置编码)
        self.pos_embed = nn.Parameter(torch.zeros(1, freq_bins, embed_dim))

        # 一个基础的 TransformerEncoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=nhead,
            dim_feedforward=embed_dim*4,  # 前馈层维度可调
            dropout=dropout,
            activation='relu'
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers
        )

        # 输出层，把 pooled 后的向量 -> 目标参数维度
        self.fc_out = nn.Linear(embed_dim, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch_size, 2*freq_bins)
        return: (batch_size, output_size)
        """
        bsz = x.shape[0]

        # 1. reshape 成 (batch_size, freq_bins, 2)
        #    每个 token 是 (实部, 虚部)
        x = x.view(bsz, self.freq_bins, 2)  

        # 2. 投影到 embed_dim: (batch_size, freq_bins, embed_dim)
        x_embed = self.input_embed(x)

        # 3. 加上可学习的位置编码
        #    pos_embed shape = (1, freq_bins, embed_dim)，可自动broadcast到 (batch_size, freq_bins, embed_dim)
        x_embed = x_embed + self.pos_embed

        # 4. TransformerEncoder 期望输入形状是 (seq_len, batch_size, embed_dim),
        #    所以需要 transpose(0,1)
        #    这里 seq_len = freq_bins
        x_embed = x_embed.transpose(0, 1)  # (freq_bins, batch_size, embed_dim)

        # 5. 送入 transformer encoder
        #    输出也是 (seq_len, batch_size, embed_dim)
        x_enc = self.transformer_encoder(x_embed)  

        # 6. 池化 or 取某个 token 作为全局特征
        #    这里用平均池化(也可以取 x_enc[0] 当作类似 [CLS] token)
        #    => (batch_size, embed_dim)
        x_global = x_enc.mean(dim=0)  # 在 seq_len 上 average

        # 7. 最终映射到 output_size
        out = self.fc_out(x_global)  # (batch_size, output_size)

        return out

def example_training():
    """
    使用连续域形式训练一个滤波器，使其逼近一个二阶带通滤波器的目标频响。
    """
    # 1. 先定义频率点
    freq_bins = 100
    # 这里的频率是线性取样或对数取样都可以，下面示例用 logspace
    freqs_hz = torch.logspace(1, 4, freq_bins)
    # 目标角频率向量
    w_target = 2 * math.pi * freqs_hz

    # 2. 生成目标频响 H_target
    #   这里的例子: 带通滤波器 H(s) = s / (s^2 + 2*zeta*omega0*s + (omega0^2))
    #   其中 s = j*w, 带通中心频率 omega0, 阻尼 zeta
    omega0 = 2 * math.pi * 200
    zeta = 0.707
    s = 1j * w_target
    # H_target = s / (s**2 + 2*zeta*omega0*s + omega0**2)
    H_target = omega0**2 / (s**2 + 2*zeta*omega0*s + omega0**2)

    # 3. 定义并联/串联数
    N, M = 1, 3
    sos_network = SOSConnect(num_parallel=N, num_series=M)

    # 每个 SOS 有 7 个参数: b0, b1, b2, a0, a1, a2, gate
    param_per_sos = 7
    total_sos = N * M

    # 4. 定义预测网络
    #   输入：这里简单起见，用目标频响的实部+虚部拼接为特征 (2*freq_bins)
    #   输出：就是所有 SOS 的参数 (total_sos * 7)
    predictor = ParamPredictorTransformer(freq_bins=freq_bins, 
                                      output_size=total_sos*param_per_sos)

    optimizer = optim.Adam(predictor.parameters(), lr=1e-3)

    # 准备训练输入: 目标频响的实部和虚部
    H_target_real, H_target_imag = H_target.real, H_target.imag
    input_feature = torch.cat([H_target_real, H_target_imag], dim=0).unsqueeze(0)

    # 训练循环
    num_steps = 20000
    lambda_reg = 0.00   # 用于门控正则，鼓励 gate 走向 0/1
    lambda_gate = 0.00  # 这里也可以加大，鼓励使用更少的 gate=1

    for step in range(num_steps):
        optimizer.zero_grad()
        # (total_sos, 7)
        pred_params = predictor(input_feature).view(total_sos, param_per_sos)

        # 处理 gate 参数：让 gate 用 sigmoid 映射到 (0,1)
        other_params = pred_params[:, :6]
        gates = torch.sigmoid(pred_params[:, 6])
        pred_params_processed = torch.cat([other_params, gates.unsqueeze(1)], dim=1)

        # 计算网络输出的滤波器频响
        H_pred = sos_network.freq_response(w_target, pred_params_processed)

        # 计算损失(示例里采用对数幅度的 MSE)
        # 避免 log(0)，可以加一点很小的 epsilon
        eps = 1e-12
        # loss_main = torch.mean(
        #     (torch.log(torch.abs(H_pred) + eps) - torch.log(torch.abs(H_target) + eps))**2
        #  )
        loss_main = torch.mean(torch.abs(H_pred - H_target)**2)


        # 添加正则项: 希望 gates 更“二值化”，即在 0 或 1 左右
        reg_loss = torch.sum(gates * (1 - gates))  # gates*(1-gates)在0和1时为0

        # 如果还想鼓励使用更少的gate=1，可以加上对 sum(gates) 的惩罚
        # 例如鼓励 sum(gates)≈1(只用一个SOS)
        gate_count = torch.abs(torch.sum(gates) - 1)

        loss = loss_main + lambda_reg * reg_loss + lambda_gate * gate_count
        loss.backward()
        optimizer.step()

        if step % 200 == 0:
            print(f"Step {step}, Loss: {loss.item():.6f}")

    # 训练完后，将 gates 二值化
    with torch.no_grad():
        final_params = predictor(input_feature).view(total_sos, param_per_sos)
        origin_params = final_params.clone()

        gates = torch.sigmoid(final_params[:, 6])
        origin_params[:, 6] = gates

        # 二值化门控
        binary_gates = (gates > 0.5).float()
        final_params[:, 6] = binary_gates
        print(f'Final gates: {binary_gates}')

    # 进一步验证: 用二值化 gates 后的参数计算频响
    H_pred_final = sos_network.freq_response(w_target, final_params)
    # 不做二值化(仅sigmoid)的结果
    H_pred_no_gate = sos_network.freq_response(w_target, origin_params)

    # 画图比较
    plt.figure(figsize=(8,5))
    plt.plot(freqs_hz.numpy(), torch.abs(H_pred_final).numpy(), 
             label="Predicted (Binary Gate)", marker='o')
    plt.plot(freqs_hz.numpy(), torch.abs(H_target).numpy(), 
             label="Target")
    plt.plot(freqs_hz.numpy(), torch.abs(H_pred_no_gate).numpy(), 
             label="Predicted (Sigmoid Gate)")
    plt.xscale('log'); plt.yscale('log')
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    example_training()
