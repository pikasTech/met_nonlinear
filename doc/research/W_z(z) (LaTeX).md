W_z(z) (LaTeX):
$$
\frac{S f \zeta \left(T^{2} f_{1}^{2} \pi^{2} - 2 T f_{1} \pi \zeta_{1} + z^{2} \left(T^{2} f_{1}^{2} \pi^{2} + 2 T f_{1} \pi \zeta_{1} + 1\right) + 2 z \left(T^{2} f_{1}^{2} \pi^{2} - 1\right) + 1\right)}{S_{1} f_{1} \zeta_{1} \left(T^{2} f^{2} \pi^{2} - 2 T f \pi \zeta + z^{2} \left(T^{2} f^{2} \pi^{2} + 2 T f \pi \zeta + 1\right) + 2 z \left(T^{2} f^{2} \pi^{2} - 1\right) + 1\right)}
$$

双线性变换后：
$$
\frac{S f \zeta \left(T^{2} f_{1}^{2} \pi^{2} - 2 T f_{1} \pi \zeta_{1} + z^{2} \left(T^{2} f_{1}^{2} \pi^{2} + 2 T f_{1} \pi \zeta_{1} + 1\right) + 2 z \left(T^{2} f_{1}^{2} \pi^{2} - 1\right) + 1\right)}{S_{1} f_{1} \zeta_{1} \left(T^{2} f^{2} \pi^{2} - 2 T f \pi \zeta + z^{2} \left(T^{2} f^{2} \pi^{2} + 2 T f \pi \zeta + 1\right) + 2 z \left(T^{2} f^{2} \pi^{2} - 1\right) + 1\right)}
$$
分子：
$$
S f \zeta \left(T^{2} f_{1}^{2} \pi^{2} - 2 T f_{1} \pi \zeta_{1} + z^{2} \left(T^{2} f_{1}^{2} \pi^{2} + 2 T f_{1} \pi \zeta_{1} + 1\right) + 2 z \left(T^{2} f_{1}^{2} \pi^{2} - 1\right) + 1\right)
$$
分母:
$$
S_{1} f_{1} \zeta_{1} \left(T^{2} f^{2} \pi^{2} - 2 T f \pi \zeta + z^{2} \left(T^{2} f^{2} \pi^{2} + 2 T f \pi \zeta + 1\right) + 2 z \left(T^{2} f^{2} \pi^{2} - 1\right) + 1\right)
$$
展开后的分子：
$$
S T^{2} f f_{1}^{2} \pi^{2} \zeta - 2 S T f f_{1} \pi \zeta \zeta_{1} + S f \zeta + z^{2} \left(S T^{2} f f_{1}^{2} \pi^{2} \zeta + 2 S T f f_{1} \pi \zeta \zeta_{1} + S f \zeta\right) + z \left(2 S T^{2} f f_{1}^{2} \pi^{2} \zeta - 2 S f \zeta\right)
$$
展开后的分母：
$$
S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} - 2 S_{1} T f f_{1} \pi \zeta \zeta_{1} + S_{1} f_{1} \zeta_{1} + z^{2} \left(S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} + 2 S_{1} T f f_{1} \pi \zeta \zeta_{1} + S_{1} f_{1} \zeta_{1}\right) + z \left(2 S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} - 2 S_{1} f_{1} \zeta_{1}\right)
$$
传递函数：
$$
\frac{S T^{2} f f_{1}^{2} \pi^{2} \zeta - 2 S T f f_{1} \pi \zeta \zeta_{1} + S f \zeta + z^{2} \left(S T^{2} f f_{1}^{2} \pi^{2} \zeta + 2 S T f f_{1} \pi \zeta \zeta_{1} + S f \zeta\right) + z \left(2 S T^{2} f f_{1}^{2} \pi^{2} \zeta - 2 S f \zeta\right)}{S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} - 2 S_{1} T f f_{1} \pi \zeta \zeta_{1} + S_{1} f_{1} \zeta_{1} + z^{2} \left(S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} + 2 S_{1} T f f_{1} \pi \zeta \zeta_{1} + S_{1} f_{1} \zeta_{1}\right) + z \left(2 S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} - 2 S_{1} f_{1} \zeta_{1}\right)}
$$

最终传递函数（手动）：

$$
\frac{S T^{2} f f_{1}^{2} \pi^{2} \zeta + 2 S T f f_{1} \pi \zeta \zeta_{1} + S f \zeta + \left(2 S T^{2} f f_{1}^{2} \pi^{2} \zeta - 2 S f \zeta\right)z^{-1} + \left(S T^{2} f f_{1}^{2} \pi^{2} \zeta - 2 S T f f_{1} \pi \zeta \zeta_{1} + S f \zeta \right)z^{-2}}{S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} + 2 S_{1} T f f_{1} \pi \zeta \zeta_{1} + S_{1} f_{1} \zeta_{1} + \left(2 S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} - 2 S_{1} f_{1} \zeta_{1}\right)z^{-1} + \left(S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} - 2 S_{1} T f f_{1} \pi \zeta \zeta_{1} + S_{1} f_{1} \zeta_{1}\right)z^{-2}}
$$

a0 归一化：a0 = $S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} + 2 S_{1} T f f_{1} \pi \zeta \zeta_{1} + S_{1} f_{1} \zeta_{1}$

$$
\frac{\frac{S T^{2} f f_{1}^{2} \pi^{2} \zeta + 2 S T f f_{1} \pi \zeta \zeta_{1} + S f \zeta}{S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} + 2 S_{1} T f f_{1} \pi \zeta \zeta_{1} + S_{1} f_{1} \zeta_{1}} + \frac{2 S T^{2} f f_{1}^{2} \pi^{2} \zeta - 2 S f \zeta}{S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} + 2 S_{1} T f f_{1} \pi \zeta \zeta_{1} + S_{1} f_{1} \zeta_{1}}z^{-1} + \frac{S T^{2} f f_{1}^{2} \pi^{2} \zeta - 2 S T f f_{1} \pi \zeta \zeta_{1} + S f \zeta}{S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} + 2 S_{1} T f f_{1} \pi \zeta \zeta_{1} + S_{1} f_{1} \zeta_{1}}z^{-2}}{1 + \frac{2 S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} - 2 S_{1} f_{1} \zeta_{1}}{S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} + 2 S_{1} T f f_{1} \pi \zeta \zeta_{1} + S_{1} f_{1} \zeta_{1}}z^{-1} + \frac{S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} - 2 S_{1} T f f_{1} \pi \zeta \zeta_{1} + S_{1} f_{1} \zeta_{1}}{S_{1} T^{2} f^{2} f_{1} \pi^{2} \zeta_{1} + 2 S_{1} T f f_{1} \pi \zeta \zeta_{1} + S_{1} f_{1} \zeta_{1}}z^{-2}}
$$

替换变量

$$
\frac{\frac{\hat{S_{\text{n}}} T^{2} \hat{f_{\text{n}}} f_{\text{n},m}^{2} \pi^{2} \zeta + 2 \hat{S_{\text{n}}} T \hat{f_{\text{n}}} f_{\text{n},m} \pi \zeta \zeta_{1} + \hat{S_{\text{n}}} \hat{f_{\text{n}}} \zeta}{S_{\text{n},m} T^{2} \hat{f_{\text{n}}}^{2} f_{\text{n},m} \pi^{2} \zeta_{1} + 2 S_{\text{n},m} T \hat{f_{\text{n}}} f_{\text{n},m} \pi \zeta \zeta_{1} + S_{\text{n},m} f_{\text{n},m} \zeta_{1}} + \frac{2 \hat{S_{\text{n}}} T^{2} \hat{f_{\text{n}}} f_{\text{n},m}^{2} \pi^{2} \zeta - 2 \hat{S_{\text{n}}} \hat{f_{\text{n}}} \zeta}{S_{\text{n},m} T^{2} \hat{f_{\text{n}}}^{2} f_{\text{n},m} \pi^{2} \zeta_{1} + 2 S_{\text{n},m} T \hat{f_{\text{n}}} f_{\text{n},m} \pi \zeta \zeta_{1} + S_{\text{n},m} f_{\text{n},m} \zeta_{1}}z^{-1} + \frac{\hat{S_{\text{n}}} T^{2} \hat{f_{\text{n}}} f_{\text{n},m}^{2} \pi^{2} \zeta - 2 \hat{S_{\text{n}}} T \hat{f_{\text{n}}} f_{\text{n},m} \pi \zeta \zeta_{1} + \hat{S_{\text{n}}} \hat{f_{\text{n}}} \zeta}{S_{\text{n},m} T^{2} \hat{f_{\text{n}}}^{2} f_{\text{n},m} \pi^{2} \zeta_{1} + 2 S_{\text{n},m} T \hat{f_{\text{n}}} f_{\text{n},m} \pi \zeta \zeta_{1} + S_{\text{n},m} f_{\text{n},m} \zeta_{1}}z^{-2}}{1 + \frac{2 S_{\text{n},m} T^{2} \hat{f_{\text{n}}}^{2} f_{\text{n},m} \pi^{2} \zeta_{1} - 2 S_{\text{n},m} f_{\text{n},m} \zeta_{1}}{S_{\text{n},m} T^{2} \hat{f_{\text{n}}}^{2} f_{\text{n},m} \pi^{2} \zeta_{1} + 2 S_{\text{n},m} T \hat{f_{\text{n}}} f_{\text{n},m} \pi \zeta \zeta_{1} + S_{\text{n},m} f_{\text{n},m} \zeta_{1}}z^{-1} + \frac{S_{\text{n},m} T^{2} \hat{f_{\text{n}}}^{2} f_{\text{n},m} \pi^{2} \zeta_{1} - 2 S_{\text{n},m} T \hat{f_{\text{n}}} f_{\text{n},m} \pi \zeta \zeta_{1} + S_{\text{n},m} f_{\text{n},m} \zeta_{1}}{S_{\text{n},m} T^{2} \hat{f_{\text{n}}}^{2} f_{\text{n},m} \pi^{2} \zeta_{1} + 2 S_{\text{n},m} T \hat{f_{\text{n}}} f_{\text{n},m} \pi \zeta \zeta_{1} + S_{\text{n},m} f_{\text{n},m} \zeta_{1}}z^{-2}}
$$

