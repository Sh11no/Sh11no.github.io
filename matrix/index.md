# 线性代数与空间解析几何 女娲补天复习笔记


## 矩阵及其初等变换

### 概念

- 同型矩阵：A与B都是m*n矩阵，则称A与B是同型矩阵。
- 负矩阵：A的每个元换成它的相反数，记为-A
- 数量矩阵：$kI，k∈R$
- 反称矩阵：$A^T=-A$

### Conclusions

- $(AB)^T=B^TA^T$
- $(AB)^{-1}=B^{-1}A^{-1}$
- AB为对称矩阵$\iff AB=BA$
- 行初等变换左乘初等矩阵，列初等变换右乘。
- $(A^T)^{-1}=(A^{-1})^T$

## 行列式

### Conclusions

- 若行列式某两行对应元成比例， 行列式为零。
- $|A^{-1}|=\frac{1}{|A|}$
- $|A^{\star}|=|A|^{n-1}$
- 范德蒙德行列式结论：$\prod_{1≤j<i<n}(x_i-x_j)$
- $A^{\star}A=|A|I$
- A可逆$\iff R(A)=n \iff AX=0$只有零解$\iff AX=b$有唯一解
- $R(A)=R(B) \iff $ A与B等价（A与B是同型矩阵）

## 几何空间

### 概念

- 自由向量：不考虑起点的向量
- 方向角：向量与坐标轴的夹角
- 方向余弦：方向角的余弦
- 平面束：经过直线$l$的全体平面称为过$l$的平面束

### Conclusions

- $Prj_u(\vec{a}+\vec{b})=Prj_u\vec{a}+Prj_u\vec{b}$
- $[\vec{a}\ \vec{b}\ \vec{c}]=0 \iff \vec{a}\ \vec{b}\ \vec{c}$共面

## n维向量空间

### 概念

- 子空间：设$V$是$R^n$的一个非空子集合，则$V$是$R^n$的一个子空间的充分必要条件是$V$对于$R^n$的加法和数乘运算是封闭的。
- 所有向量$\vec{a_1}\ \vec{a_2}\ \vec{a_3}\ ... \vec{a_n}$线性组合的集合用$L(\vec{a_1},\vec{a_2},...,\vec{a_n})$表示。
- 只含零向量的向量组的秩为0。

### Conclusions

- $A=(\vec{a_1},\vec{a_2},...,\vec{a_n})$，则$\vec{a_1},\vec{a_2},...,\vec{a_n}$线性相关$\iff AX=0$有非零解$\iff R(A)<n\iff |A|=0$
- $R(AB)≤min\{R(A),R(B)\}$
- $R(A+B)≤R(A)+R(B)$
- $max\{R(A),R(B)\}R[(A,B)]≤R(A)+R(B)$
- $AX=0$的基础解系所含解向量个数为$n-R(A)$
- $R(A)=n-1$则$R(A^{\star})=1$

## 特征值与特征向量

### 概念

- 特征子空间：对于特征值$\lambda$的所有特征向量构成的子空间。

### Conclusions

- $\lambda$是$A$的一个特征值，则$\frac{1}{\lambda}$是$A^{-1}$的一个特征值，特征向量相同。

- 方阵的n个特征值之和等于方阵的主对角元之和，n个特征值之积等于方阵的行列式，方阵A可逆的充分必要条件是A的特征值全部不为零。

- 柯西不等式：$(\vec{a}·\vec{b})^2≤|\vec{a}|^2|\vec{b}|^2$

- 正交矩阵：

  $A^{-1}=A^T$

  $|A|=1or-1$

  $A,B$是正交矩阵，则$AB$是正交矩阵。

- 实对称矩阵的对应不同特征值的特征向量彼此正交。

## 二次型与二次曲面

### Conclusions

- 正定二次型$\iff A$的特征值全为正数$\iff A$的所有顺序主子式都大于零
- 负定二次型$\iff A$的特征值全为负数$\iff A$的顺序主子式满足$(-1)^kP_k>0$（奇负偶正）
- 正惯性指数等于正特征值个数。
