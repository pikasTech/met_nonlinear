import sympy as sp
# 定义符号变量
s, z, T, zeta, f, S, pi, zeta1, f1, S1 = sp.symbols(
    's z T zeta f S pi zeta1 f1 S1')

# 定义传递函数的分子和分母
numerator_s = S * zeta * f * \
    (s**2 + 4 * pi * zeta1 * f1 * s + (2 * pi * f1)**2)
denominator_s = S1 * zeta1 * f1 * \
    (s**2 + 4 * pi * zeta * f * s + (2 * pi * f)**2)

# 定义双线性变换公式 s = 2/T * (1 - z**(-1)) / (1 + z**(-1))
s_to_z = 2 / T * (1 - z**(-1)) / (1 + z**(-1))

# 替换分子和分母中的 s
numerator_z = numerator_s.subs(s, s_to_z)
denominator_z = denominator_s.subs(s, s_to_z)

# 展开分子和分母
numerator_z_expanded = sp.expand(numerator_z)
denominator_z_expanded = sp.expand(denominator_z)

# 合并分母中同阶的z项
denominator_z_simplified = sp.simplify(denominator_z_expanded)

# 合并分子中同阶的z项
numerator_z_simplified = sp.simplify(numerator_z_expanded)

# 进一步化简为z^n的多项式
numerator_z_polynomial = sp.collect(numerator_z_simplified, z)
denominator_z_polynomial = sp.collect(denominator_z_simplified, z)

# 输出化简后的分子 (LaTeX)
latex_numerator_polynomial = sp.latex(numerator_z_polynomial)
# print(f"化简后的分子 (LaTeX):")
# print(f"${latex_numerator_polynomial}$")
# print(f"化简后的分子: {numerator_z_polynomial}")


# 输出化简后的分母 (LaTeX)
latex_denominator_polynomial = sp.latex(denominator_z_polynomial)
# print(f"化简后的分母 (LaTeX):")
# print(f"${latex_denominator_polynomial}$")
# print(f"化简后的分母: {denominator_z_polynomial}")

# 合并为最终的传递函数
transfer_function_z_polynomial = numerator_z_polynomial / denominator_z_polynomial

# 输出 LaTeX 格式的最终传递函数
latex_transfer_function_polynomial = sp.latex(
    sp.simplify(transfer_function_z_polynomial))
print(f"最终传递函数 W_z(z) (LaTeX):")
print(f"${latex_transfer_function_polynomial}$")

print(f"最终传递函数 W_z(z):")
print(f"{transfer_function_z_polynomial}")


# 定义分子和分母
numerator = S*f*zeta*(T**2*f1**2*pi**2 - 2*T*f1*pi*zeta1 + z**2*(T**2*f1**2*pi**2 + 2*T*f1*pi*zeta1 + 1) + z*(2*T**2*f1**2*pi**2 - 2) + 1)
denominator = S1*f1*zeta1*(T**2*f**2*pi**2 - 2*T*f*pi*zeta + z**2*(T**2*f**2*pi**2 + 2*T*f*pi*zeta + 1) + z*(2*T**2*f**2*pi**2 - 2) + 1)

# 展开分子和分母
numerator_expanded = sp.expand(numerator)
denominator_expanded = sp.expand(denominator)

# 合并分母和分子中z的同阶项
numerator_collected = sp.collect(numerator_expanded, z)
denominator_collected = sp.collect(denominator_expanded, z)

# 输出展开后的结果
numerator_collected, denominator_collected
print(f"分子展开后的结果: {numerator_collected}")
print(f"分母展开后的结果: {denominator_collected}")

# 输出化简后的分子 (LaTeX)
latex_numerator_collected = sp.latex(numerator_collected)
print(f"化简后的分子 (LaTeX):")
print(f"${latex_numerator_collected}$")

# 输出化简后的分母 (LaTeX)
latex_denominator_collected = sp.latex(denominator_collected)
print(f"化简后的分母 (LaTeX):")
print(f"${latex_denominator_collected}$")

# 合并为最终的传递函数
transfer_function = numerator_collected / denominator_collected

# 输出 LaTeX 格式的最终传递函数

latex_transfer_function = sp.latex(transfer_function)

print(f"最终传递函数 W(z) (LaTeX):")

print(f"${latex_transfer_function}$")


"""
    W(z) (LaTeX):
    $\frac{2 S_{n} T f_{n} \pi z^{2} \zeta - 2 S_{n} T f_{n} \pi \zeta}{T^{2} f_{n}^{2} \pi^{2} - 2 T f_{n} \pi \zeta + z^{2} \left(T^{2} f_{n}^{2} \pi^{2} + 2 T f_{n} \pi \zeta + 1\right) + z \left(2 T^{2} f_{n}^{2} \pi^{2} - 2\right) + 1}$
"""

"""
        H_{\rm z}(z) = \frac{2 S_{n} T f_{n} \pi \zeta  z^{2} - 2 S_{n} T f_{n} \pi \zeta}{\left(T^{2} f_{n}^{2} \pi^{2} + 2 T f_{n} \pi \zeta + 1\right)z^{2}  +  \left(2 T^{2} f_{n}^{2} \pi^{2} - 2\right) z + T^{2} f_{n}^{2} \pi^{2} - 2 T f_{n} \pi \zeta + 1}
"""

"""
\frac{(2 S_{n} T f_{n} \pi \zeta) - 2 S_{n} T f_{n} \pi \zeta z^{-2}}{\left(T^{2} f_{n}^{2} \pi^{2} + 2 T f_{n} \pi \zeta + 1\right) +  \left(2 T^{2} f_{n}^{2} \pi^{2} - 2\right) z^{-1} + \left(T^{2} f_{n}^{2} \pi^{2} - 2 T f_{n} \pi \zeta + 1\right)z^{-2}}
"""
