# 板子 (Ver.诗乃)


## Tarjan&amp;Topo

```C&#43;&#43;
void tarjan(int u) {
	dfn[u] = low[u] = &#43;&#43;tim; ins[u] = 1; stac[&#43;&#43;top] = u;
	for(int v, i = h[u]; ~i; i = e[i].next)
		if(!dfn[(v = e[i].to)]) {
			tarjan(v);
			low[u] = min(low[u], low[v]);
		} else if(ins[v]) low[u] = min(low[u], low[v]);
	if(low[u] == dfn[u]) {
		int y; while(y = stac[top--]) {
            sd[y] = u; ins[y] = 0; if(u == y) break; p[u] &#43;= p[y];
        }
	}
}
void topo() {
	queue &lt;int&gt; q;
	for(int i = 1; i &lt;= n; &#43;&#43;i)
		if(sd[i] == i &amp;&amp; !in[i]) q.push(i), dis[i] = p[i];
	while(!q.empty()) {
		int u = q.front(); q.pop();
		for(int v, i = h[u]; ~i; i = e[i].next) {
				v = e[i].to;
				dis[v] = max(dis[v], dis[u] &#43; p[v]);
				--in[v]; if(!in[v]) q.push(v);
			}
	}
	int ans = 0;
	for(int i = 1; i &lt;= n; &#43;&#43;i) ans = max(ans, dis[i]);
	printf(&#34;%d\n&#34;, ans);
}
```

## ST

```C&#43;&#43;
void ST_Build() {
	for(int j = 1; j &lt;= 21; &#43;&#43;j)
		for(int i = 1; i &#43; (1 &lt;&lt; j) - 1 &lt;= n; &#43;&#43;i)
			st[i][j] = max(st[i][j-1], st[i&#43;(1&lt;&lt;(j-1))][j-1]);
}
int ST_query(int l, int r) {
	int k = lg2[r-l&#43;1];
	return max(st[l][k], st[r-(1&lt;&lt;k)&#43;1][k]);
}
```

## ST-BlackMagic

```c&#43;&#43;
struct RMQ {
	#define L(x) ((x-1)*siz&#43;1)
	#define R(x) std::min(n, x*siz&#43;1)
	#define bl(x) ((x-1)/siz&#43;1)
	const int MAXB = 2050, siz = 50;
	int prf[MAXN], suf[MAXN], n, st[MAXB][13], lg2[MAXN], a[MAXN];
	void init(int *s, int _n, int k) {
		n = _n;
		for(int i = 1; i &lt;= n; &#43;&#43;i)
            a[i] = s[i] % k, st[bl(i)][0] = min(st[bl(i)][0], a[i]);
		for(int i = 1; i &lt;= bl(n); &#43;&#43;i) {
			prf[L(i)] = a[L(i)]; suf[R(i)] = a[R(i)];
			for(int j = L(i)&#43;1; j &lt;= R(i); &#43;&#43;j) prf[j] = min(prf[j-1], a[j]);
			for(int j = R(i)-1; j &gt;= L(i); --j) suf[j] = min(suf[j&#43;1], a[j]);
		}
		for(int j = 1; j &lt;= 12; &#43;&#43;j)
			for(int i = 1; i &#43; (1 &lt;&lt; j) - 1 &lt;= bl(n); &#43;&#43;i)
				st[i][j] = min(st[i][j-1], st[i&#43;(1&lt;&lt;(j-1))][j-1]);
	}
	int QST(int l, int r) {
		if(l &gt; r) return 0; int k = lg2[r-l&#43;1];
		return min(st[l][k], st[r-(1&lt;&lt;k)&#43;1][k]);
	}
	int query(int l, int r) {
		if(bl(l) == bl(r)) {
			int res = 0;
			for(int i = l; i &lt;= r; &#43;&#43;i) res = max(res, a[i]);
			return res;
		} else return min(min(prf[r], suf[l]), QST(bl(l)&#43;1, bl(r)-1));
	}
} ST;
```

## Manacher

```c&#43;&#43;
void Manacher() {
	int mr = 0, mid;
	for(int i = 0; i &lt; n; &#43;&#43;i) {
		p[i] = i &lt; mr ? min(p[(mid &lt;&lt; 1) - i], p[mid] &#43; mid - i) : 1;
		for(; s[i-p[i]] == s[i&#43;p[i]]; &#43;&#43;p[i]);
		if(p[i] &#43; i &gt; mr) mr = i &#43; p[i], mid = i;
	}
}
int main() {
	scanf(&#34;%s&#34;, a); _n = strlen(a);
	s[0] = s[1] = &#39;#&#39;; n = 1;
	for(int i = 0; i &lt; _n; &#43;&#43;i) s[&#43;&#43;n] = a[i], s[&#43;&#43;n] = &#39;#&#39;;
	s[&#43;&#43;n] = 0; Manacher();
	for(int i = 0; i &lt; n; &#43;&#43;i) ans = max(ans, p[i]);
	printf(&#34;%d\n&#34;, ans-1);
}
```

## 线性基

```C&#43;&#43;
for(int i = 1; i &lt;= n; &#43;&#43;i) {
		read(a);
		for(int j = 50; j &gt;= 0; --j) {
			if((a &gt;&gt; j) &amp; 1) {
				if(!p[j]) {p[j] = a; break;}
				a ^= p[j];
			}
		}
	}
	for(int i = 50; i &gt;= 0; --i)
		if(p[i]) ans = max(ans, ans ^ p[i]);
```

## 线性逆元

```c&#43;&#43;
inv[1] = 1;
for(int i = 2; i &lt;= n; &#43;&#43;i)
	inv[i] = 1ll * (P - P / i) % P * inv[P % i]	% P;
```

## 后缀数组

```C&#43;&#43;
void getSA() {
	for(int i = 1; i &lt;= n; &#43;&#43;i) &#43;&#43;c[x[i] = s[i]];
	for(int i = 1; i &lt;= m; &#43;&#43;i) c[i] &#43;= c[i-1];
	for(int i = n; i &gt;= 1; --i) sa[c[x[i]]--] = i;
	for(int k = 1; k &lt;= n; k &lt;&lt;= 1) {
		int num = 0;
		for(int i = n - k &#43; 1; i &lt;= n; &#43;&#43;i) y[&#43;&#43;num] = i;
		for(int i = 1; i &lt;= n; &#43;&#43;i) if(sa[i] &gt; k) y[&#43;&#43;num] = sa[i] - k;
		memset(c, 0, sizeof c);
		for(int i = 1; i &lt;= n; &#43;&#43;i) &#43;&#43;c[x[i]];
		for(int i = 1; i &lt;= m; &#43;&#43;i) c[i] &#43;= c[i-1];
		for(int i = n; i &gt;= 1; --i) sa[c[x[y[i]]]--] = y[i], y[i] = 0;
		swap(x, y);
		x[sa[1]] = 1; num = 0;
		for(int i = 1; i &lt;= n; &#43;&#43;i)
			x[sa[i]] = (y[sa[i-1]] == y[sa[i]] &amp;&amp; y[sa[i-1]&#43;k] == y[sa[i]&#43;k]) ? num : &#43;&#43;num;
		if(num == n) break;
		m = num;
	}
}
```

## 点分治

```C&#43;&#43;
void getroot(int u, int p, int S) {
	siz[u] = 1, f[u] = 0;
	for(int v, i = h[u]; ~i; i = e[i].next)
		if((v = e[i].to) != p &amp;&amp; !vis[v])
			getroot(v, u, S), siz[u] &#43;= siz[v], f[u] = max(f[u], siz[v]);
	f[u] = max(f[u], S - siz[u]); rt = f[u] &lt; f[rt] ? u : rt;
}
void getdis(int u, int p) {
	stk[&#43;&#43;top] = dis[u];
	for(int v, i = h[u]; ~i; i = e[i].next)
		if((v = e[i].to) != p &amp;&amp; !vis[v])
			dis[v] = dis[u] &#43; e[i].w, getdis(v, u);
}
void solve(int u, int w, int t) {
	top = 0, dis[u] = w, getdis(u, 0);
	for(int i = 1; i &lt;= top; &#43;&#43;i)
		for(int j = 1; j &lt;= top; &#43;&#43;j)
			if(i != j) ans[stk[i] &#43; stk[j]] &#43;= t;
}
void devide(int u) {
	solve(u, 0, 1); vis[u] = 1;
	for(int v, i = h[u]; ~i; i = e[i].next)
		if(!vis[(v = e[i].to)]) {
			solve(v, e[i].w, -1), rt = 0, f[0] = n;
			getroot(v, u, siz[u]), devide(rt);
		}
}
```

## 线段树

```C&#43;&#43;
#define L(u) (u&lt;&lt;1)
#define R(u) (u&lt;&lt;1|1)
#define mid ((l&#43;r)&gt;&gt;1)
void PU(int u) {t[u] = (t[L(u)] &#43; t[R(u)]) % P;}
void ADD(int u, int l, int r, int k) {
	t[u] &#43;= (r - l &#43; 1) * k % P; t[u] %= P; add[u] = (add[u] &#43; k) % P;
}
void MUL(int u, int l, int r, int k) {
	t[u] = t[u] * k % P; add[u] = add[u] * k % P; mul[u] = mul[u] * k % P;
}
void PD(int u, int l, int r) {
	MUL(L(u), l, mid, mul[u]); MUL(R(u), mid&#43;1, r, mul[u]); mul[u] = 1;
	ADD(L(u), l, mid, add[u]); ADD(R(u), mid&#43;1, r, add[u]); add[u] = 0;
}
void build(int u, int l, int r) {
	mul[u] = 1; if(l == r) {t[u] = a[l]; return;}
	build(L(u), l, mid); build(R(u), mid&#43;1, r); PU(u);
}
void MA(int u, int l, int r, int tl, int tr, int k) {
	if(tr &lt; l || tl &gt; r) return;
	if(tl &lt;= l &amp;&amp; r &lt;= tr) {ADD(u, l, r, k); return;}
	PD(u, l, r); MA(L(u), l, mid, tl, tr, k); MA(R(u), mid&#43;1, r, tl, tr, k); PU(u);
}
void MM(int u, int l, int r, int tl, int tr, int k) {
	if(tr &lt; l || tl &gt; r) return;
	if(tl &lt;= l &amp;&amp; r &lt;= tr) {MUL(u, l, r, k); return;}
	PD(u, l, r); MM(L(u), l, mid, tl, tr, k); MM(R(u), mid&#43;1, r, tl, tr, k); PU(u);
}
int Q(int u, int l, int r, int tl, int tr) {
	if(tr &lt; l || tl &gt; r) return 0; if(tl &lt;= l &amp;&amp; r &lt;= tr) return t[u];
	PD(u, l, r); return (Q(L(u), l, mid, tl, tr) &#43; Q(R(u), mid&#43;1, r, tl, tr)) % P;
}
```

## 三分

```C&#43;&#43;
while(fabs(r-l) &gt;= eps) {
	double mid = (l &#43; r) / 2;
	if(f(mid - eps) &lt; f(mid &#43; eps)) l = mid;
	else r = mid;
}
```

## 树状数组

```c&#43;&#43;
void U(int x, int k) {for(; x &lt;= n; t[x] &#43;= k, x &#43;= x&amp;-x);}
int Q(int x) {int w = 0; for(; x; w &#43;= t[x], x -= x&amp;-x); return w;}
```

## 高斯消元

```C&#43;&#43;
for(int i = 1; i &lt;= n; &#43;&#43;i) {
	int p = i;
	for(int j = i &#43; 1; j &lt;= n; &#43;&#43;j)
		if(fabs(a[j][i]) &gt; fabs(a[p][i])) p = j;
	if(a[p][i] == 0) {puts(&#34;No Solution&#34;); return 0;}
	for(int j = 1; j &lt;= n&#43;1; &#43;&#43;j) swap(a[i][j], a[p][j]);
	for(int j = 1; j &lt;= n; &#43;&#43;j) {
		if(i == j) continue;
		double t = a[j][i] / a[i][i];
		for(int k = i; k &lt;= n&#43;1; &#43;&#43;k) a[j][k] -= a[i][k] * t;
	}
}
for(int i = 1; i &lt;= n; &#43;&#43;i) printf(&#34;%.2lf\n&#34;, a[i][n&#43;1] / a[i][i]);
```

## 最小生成树&amp;并查集

```C&#43;&#43;
int findfa(int x) {return x == fa[x] ? x : fa[x] = findfa(fa[x]);}
int main() {
	for(int i = 1; i &lt;= n; &#43;&#43;i) fa[i] = i;
	sort(e&#43;1, e&#43;m&#43;1);
	for(int i = 1; i &lt;= m; &#43;&#43;i) {
		int x = findfa(e[i].u), y = findfa(e[i].v);
		if(x == y) continue;
		ans &#43;= e[i].w; &#43;&#43;cnt;
		if(cnt == n-1) break;
		fa[x] = y;
	}
}
```

## DINIC

```C&#43;&#43;
bool bfs() {
	memset(d, -1, sizeof d); queue &lt;int&gt; q; q.push(s); d[s] = 0;
	while(!q.empty()) {
		int u = q.front(); q.pop();
		for(int v, i = h[u]; ~i; i = e[i].next)
			if(d[v = e[i].to] == -1 &amp;&amp; e[i].w &gt; 0)
				d[v] = d[u] &#43; 1, q.push(v);
	}
	return d[t] != -1;
}
int dfs(int u, int f) {
	int r = 0;
	if(u == t) return f;
	for(int v, i = h[u]; ~i &amp;&amp; r &lt; f; i = e[i].next)
		if(d[(v = e[i].to)] == d[u] &#43; 1 &amp;&amp; e[i].w &gt; 0) {
			int x = dfs(v, min(e[i].w, f-r));
			e[i].w -= x; e[i^1].w &#43;= x; r &#43;= x;
		}
	if(!r) d[u] = -1; return r;
}
int dinic() {
	int x, ans = 0;
	while(bfs()) while(x = dfs(s, 1e9)) ans &#43;= x;
	return ans;
}
```

## 线性筛

```C&#43;&#43;
for(int i = 2; i &lt;= n; &#43;&#43;i) {
	if(!notp[i]) p[&#43;&#43;cntp] = i;
	for(int j = 1; 1ll*i*p[j] &lt;= n &amp;&amp; j &lt;= cntp; &#43;&#43;j) {
		notp[i*p[j]] = 1;
		if(i % p[j] == 0) break;
	}
}
```

## 左偏树

```C&#43;&#43;
int F(int x) {return x == fa[x] ? x : fa[x] = F(fa[x]);}
int Merge(int x, int y) {
	if(x*y == 0) return x&#43;y;
	if(v[x] &gt; v[y] || (v[x] == v[y] &amp;&amp; x &gt; y)) swap(x, y);
	R(x) = Merge(R(x), y); fa[R(x)] = fa[L(x)] = x;
	if(dis[R(x)] &gt; dis[L(x)]) swap(L(x), R(x));
	dis[x] = dis[R(x)] &#43; 1; return x;
}
int Top(int x) {return del[x] ? -1 : v[x];}
void Pop(int x) {
	if(del[x]) return; del[x] = 1;
	fa[L(x)] = L(x); fa[R(x)] = R(x);
	fa[x] = Merge(L(x), R(x));
}
```

## LCT

```c&#43;&#43;
bool nroot(int x) {return ch[fa[x]][0] == x || ch[fa[x]][1] == x;}
void pushup(int x) {sumx[x] = sumx[ch[x][1]] ^ sumx[ch[x][0]] ^ val[x];} 
void pushr(int x) {swap(ch[x][1], ch[x][0]); rot[x] ^= 1;}
void pushdown(int x) {if(rot[x]) {if(ch[x][0]) pushr(ch[x][0]); if(ch[x][1]) pushr(ch[x][1]); rot[x] = 0;}}
void rotate(int x) {
	int y = fa[x], z = fa[y], k = (x == ch[y][1]);
	if(nroot(y)) ch[z][(y == ch[z][1])] = x; fa[x] = z;
	ch[y][k] = ch[x][k^1]; if(ch[x][k^1]) fa[ch[x][k^1]] = y;
	ch[x][k^1] = y; fa[y] = x; pushup(y);
}
void splay(int x) {
	int y = x, z = 0; st[&#43;&#43;z] = y;
	while(nroot(y)) st[&#43;&#43;z] = y = fa[y]; while(z) pushdown(st[z--]);
	for(int y; nroot(x); rotate(x)) if(nroot(y = fa[x])) rotate((y == ch[fa[y]][0]) ^ (x == ch[y][0]) ? x : y);
	pushup(x);
}
void access(int x) {for(int y = 0; x; x = fa[y = x]) splay(x), ch[x][1] = y, pushup(x);}
void makeroot(int x) {access(x); splay(x); pushr(x);}
int findroot(int x) {access(x); splay(x); for(; ch[x][0]; x = ch[x][0]) pushdown(x); splay(x); return x;}
void spilit(int x, int y) {makeroot(x); access(y); splay(y);}
void link(int x, int y) {makeroot(x); if(findroot(y) != x) fa[x] = y;}
void cut(int x, int y) {makeroot(x); if(findroot(y) == x &amp;&amp; fa[y] == x &amp;&amp; !ch[y][0]) {fa[y] = ch[x][1] = 0; pushup(x);}}
```

## KMP

```C&#43;&#43;
for(int i = 2, j = 0; i &lt;= n; &#43;&#43;i) {
	while(j &amp;&amp; s[i] != s[j&#43;1]) j = nxt[j];
	if(s[j&#43;1] == s[i]) &#43;&#43;j; nxt[i] = j;
}
for(int i = 1, j = 0; i &lt;= m; &#43;&#43;i) {
	while(j &gt; 0 &amp;&amp; t[i] != s[j&#43;1]) j = nxt[j];
	if(s[j&#43;1] == t[i]) &#43;&#43;j;
	if(j == n) printf(&#34;%d\n&#34;, i-n&#43;1);
}
```

## SAM

```C&#43;&#43;
struct SoumAsuMire {
	int ch[MAXN][26], fa[MAXN], last, cnt, len[MAXN];
	void insert(int c) {
		int p = last, np = &#43;&#43;cnt; last = np; len[np] = len[p] &#43; 1;
		for(; p &amp;&amp; !ch[p][c]; ch[p][c] = np, p = fa[p]);
		if(!p) fa[np] = 1;
		else {
			int q = ch[p][c];
			if(len[q] == len[p] &#43; 1) fa[np] = q;
			else {
				int nq = &#43;&#43;cnt; len[nq] = len[p] &#43; 1;
				memcpy(ch[nq], ch[q], sizeof ch[q]);
				fa[nq] = fa[q]; fa[q] = fa[np] = nq;
				for(; p &amp;&amp; ch[p][c] == q; ch[p][c] = nq, p = fa[p]);
			}
		}
	}
	void build(char *s) {
		int n = strlen(s&#43;1); last = 1;
		for(int i = 1; i &lt;= n; &#43;&#43;i) insert(s[i] - &#39;a&#39;);
	}
	int getans() {
		int ans = 0;
		for(int i = 2; i &lt;= cnt; &#43;&#43;i) ans &#43;= len[i] - len[fa[i]];
		return ans;
	}
} SAM;
```

## LCA(ST)

```C&#43;&#43;
void dfsRMQ(int u, int p) {
	st[&#43;&#43;idx][0] = u; dfn[u] = idx; dep[u] = dep[p] &#43; 1;
	for(int v, i = h[u]; ~i; i = e[i].next)
		if((v = e[i].to) != p) dfsRMQ(v, u), st[&#43;&#43;idx][0] = u;
}
void LCAinit() {
	for(int i = 2; i &lt;= (n &lt;&lt; 1); &#43;&#43;i) lg2[i] = lg2[i&gt;&gt;1] &#43; 1;
	dep[1] = 1; dfsRMQ(rt, 0);
	for(int j = 1; j &lt; 20; &#43;&#43;j)
		for(int i = 1; i &#43; (1 &lt;&lt; j) &lt;= (n &lt;&lt; 1); &#43;&#43;i)
			st[i][j] = Min(st[i][j-1], st[i&#43;(1&lt;&lt;(j-1))][j-1]);
}
int LCA(int x, int y) {
	x = dfn[x]; y = dfn[y];
	if(x &gt; y) swap(x, y);
	int k = lg2[y-x&#43;1];
	return Min(st[x][k], st[y-(1&lt;&lt;k)&#43;1][k]);
}
```

## mcmf

```C&#43;&#43;
bool SPFA() {
	memset(d, 63, sizeof d); memset(vis, 0, sizeof vis); memset(flow, 63, sizeof flow);
	queue &lt;int&gt; q; q.push(s); d[s] = 0; vis[s] = 1;
	while(!q.empty()) {
		int u = q.front(); q.pop(); vis[u] = 0;
		for(int v, i = h[u]; ~i; i = e[i].next)
			if(d[v = e[i].to] &gt; d[u] &#43; e[i].c &amp;&amp; e[i].f) {
				d[v] = d[u] &#43; e[i].c; pos[v] = i;
				fa[v] = u; flow[v] = min(flow[u], e[i].f);
				if(!vis[v]) vis[v] = 1, q.push(v);
			}
	} return flow[s] != flow[t];
}
void mcmf() {
	while(SPFA()) {
		mc &#43;= flow[t]; mf &#43;= flow[t] * d[t];
		for(int u = t; u != s; u = fa[u]) e[pos[u]].f -= flow[t], e[pos[u]^1].f &#43;= flow[t];
	}
}
```

## AC自动机

```c&#43;&#43;
#include &lt;bits/stdc&#43;&#43;.h&gt;
using namespace std;
const int S = 2000050, T = 200050;
struct Edge {int to, next;} e[T];
char s[S]; int n, h[T], cnt, ch[T][26], fail[T], match[T], siz[T], tot = 1, en;
queue &lt;int&gt; q;
void addedge(int u, int v) {e[en] = (Edge) {v, h[u]}; h[u] = en&#43;&#43;;}
void dfs(int u) {
	for(int v, i = h[u]; ~i; i = e[i].next)
		dfs(v = e[i].to), siz[u] &#43;= siz[v];
}
int main() {
	scanf(&#34;%d&#34;, &amp;n); memset(h, -1, sizeof h);
	for(int i = 1; i &lt;= n; &#43;&#43;i) {
		scanf(&#34;%s&#34;, s); int u = 1, j;
		for(u = 1, j = 0; s[j]; &#43;&#43;j) {
			int c = s[j] - &#39;a&#39;;
			if(!ch[u][c]) ch[u][c] = &#43;&#43;tot;
			u = ch[u][c];
		} match[i] = u;
	}
	for(int i = 0; i &lt; 26; &#43;&#43;i) ch[0][i] = 1;
	q.push(1);
	while(!q.empty()) {
		int u = q.front(); q.pop();
		for(int i = 0; i &lt; 26; &#43;&#43;i) 
			if(ch[u][i]) {
				fail[ch[u][i]] = ch[fail[u]][i];
				q.push(ch[u][i]);
			} else ch[u][i] = ch[fail[u]][i];
	}
	scanf(&#34;%s&#34;, s);
	for(int u = 1, i = 0; s[i]; &#43;&#43;i) &#43;&#43;siz[u = ch[u][s[i]-&#39;a&#39;]];
	for(int i = 2; i &lt;= tot; &#43;&#43;i) addedge(fail[i], i); dfs(1);
	for(int i = 1; i &lt;= n; &#43;&#43;i) printf(&#34;%d\n&#34;, siz[match[i]]);
	puts(&#34;&#34;);
}
```

## dijkstra

```C&#43;&#43;
void dijkstra() {
	memset(d, 0x3f, sizeof d);
	d[s] = 0; q.push((D) {s, 0});
	while(!q.empty()) {
		int u = q.top().u; q.pop();
		if(vis[u]) continue; vis[u] = 1;
		for(int v, i = h[u]; ~i; i = e[i].next)
			if(d[v = e[i].to] &gt; d[u] &#43; e[i].w) {
				d[v] = d[u] &#43; e[i].w;
				if(!vis[v]) q.push((D) {v, d[v]});
			}
	}
}
```

## 树哈希

```C&#43;&#43;
ull Hash(int u, int p) {
	ull q[MAXN], ans = X; int top = 0;
	for(int i = h[u]; ~i; i = e[i].next)
		if(e[i].to != p) q[&#43;&#43;top] = Hash(e[i].to, u);
	sort(q&#43;1, q&#43;top&#43;1);
	for(int i = 1; i &lt;= top; &#43;&#43;i) ans = ans * P &#43; q[i];
	return ans * P &#43; X &#43; 1;
}
```

## CDQ分治

```c&#43;&#43;
struct BITS {
	int t[MAXN];
	void U(int x, int k) {for(; x &lt;= m; t[x] &#43;= k, x &#43;= x&amp;-x);}
	int Q(int x) {int res = 0; for(; x; res &#43;= t[x], x -= x&amp;-x); return res;}
} T;
void cdq(int l, int r) {
	if(l == r) return; int mid = (l &#43; r) &gt;&gt; 1;
	cdq(l, mid); cdq(mid&#43;1, r);
	sort(a&#43;l, a&#43;mid&#43;1, cmpy); sort(a&#43;mid&#43;1, a&#43;r&#43;1, cmpy);
	int i = mid &#43; 1, j = l;
	for(; i &lt;= r; &#43;&#43;i) {
		for(; a[j].y &lt;= a[i].y &amp;&amp; j &lt;= mid; &#43;&#43;j) T.U(a[j].z, a[j].w);
		a[i].ans &#43;= T.Q(a[i].z);
	} for(int k = l; k &lt; j; &#43;&#43;k) T.U(a[k].z, -a[k].w);
}
int main() {
	read(_n); read(m);
	for(int i = 1; i &lt;= _n; &#43;&#43;i) read(b[i].x), read(b[i].y), read(b[i].z);
	sort(b&#43;1, b&#43;_n&#43;1, cmpx);
	for(int c = 0, i = 1; i &lt;= _n; &#43;&#43;i) {
		&#43;&#43;c;
		if(b[i].x != b[i&#43;1].x || b[i].y != b[i&#43;1].y || b[i].z != b[i&#43;1].z)
			a[&#43;&#43;n] = b[i], a[n].w = c, c = 0;
	} cdq(1, n);
	for(int i = 1; i &lt;= n; &#43;&#43;i) cnt[a[i].ans &#43; a[i].w - 1] &#43;= a[i].w;
	for(int i = 0; i &lt; _n; &#43;&#43;i) printf(&#34;%d\n&#34;, cnt[i]);
}
```

## Lucas

```C&#43;&#43;
int C(int n, int m) {
	if(m &gt; n) return 0;
	return 1ll * fac[n] * power(fac[m], P-2) * power(fac[n-m], P-2);
}
int Lucas(int n, int m) {
	if(m == 0) return 1;
	return 1ll * C(n%P, m%P) * Lucas(n/P, m/P) % P;
}
```

## 二分图

```c&#43;&#43;
bool dfs(int u) {
	for(int v, i = h[u]; ~i; i = e[i].next) {
		if(vis[v = e[i].to] != tag) {
			vis[v] = tag;
			if(!match[v] || dfs(match[v])) {
				match[v] = u; return 1;
			}
		}
	} return 0;
}
```

## 莫队二次离线

```c&#43;&#43;
#include &lt;bits/stdc&#43;&#43;.h&gt;
using namespace std;
const int MAXN = 100050;
typedef long long lint;
void read(int &amp;x) {
	char ch; while(ch = getchar(), ch &lt; &#39;!&#39;); x = ch - 48;
	while(ch = getchar(), ch &gt; &#39;!&#39;) x = (x &lt;&lt; 3) &#43; (x &lt;&lt; 1) &#43; ch - 48;
}
struct Qry {int l, r, id; lint ans;} q[MAXN];
struct T{int l, r, id;};
int n, m, a[MAXN], siz[MAXN], k, blsz, bl[MAXN], t[MAXN], pref[MAXN];
vector &lt;int&gt; buc; vector &lt;T&gt; v[MAXN]; lint ans[MAXN];
int cmp(Qry a, Qry b) {return bl[a.l] == bl[b.l] ? a.r &lt; b.r : a.l &lt; b.l;}
int main() {
	read(n); read(m); read(k); blsz = sqrt(n);
	if(k &gt; 14) {for(int i = 1; i &lt;= m; &#43;&#43;i) puts(&#34;0&#34;); return 0;}
	for(int i = 1; i &lt;= n; &#43;&#43;i) read(a[i]);
	for(int i = 0; i &lt; 16384; &#43;&#43;i) if((siz[i] = siz[(i&gt;&gt;1)] &#43; (i&amp;1)) == k) buc.push_back(i);
	for(int i = 1; i &lt;= m; &#43;&#43;i) read(q[i].l), read(q[i].r), q[i].id = i;
	for(int i = 1; i &lt;= n; &#43;&#43;i) bl[i] = (i-1) / blsz &#43; 1;
	sort(q&#43;1, q&#43;m&#43;1, cmp);
	for(int i = 1; i &lt;= n; &#43;&#43;i) {
		for(int j = 0; j &lt; buc.size(); &#43;&#43;j) &#43;&#43;t[a[i]^buc[j]];
		pref[i] = t[a[i&#43;1]];
	}
	for(int L = 1, R = 0, i = 1; i &lt;= m; &#43;&#43;i) {
		int l = q[i].l, r = q[i].r;
		   if(L &lt; l) v[R].push_back((T) {L, l-1, -i});
		while(L &lt; l) {q[i].ans &#43;= pref[L-1]; &#43;&#43;L;}
		   if(L &gt; l) v[R].push_back((T) {l, L-1, i});
		while(L &gt; l) {q[i].ans -= pref[L-2]; --L;}
		   if(R &lt; r) v[L-1].push_back((T) {R&#43;1, r, -i});
		while(R &lt; r) {q[i].ans &#43;= pref[R]; &#43;&#43;R;}
		   if(R &gt; r) v[L-1].push_back((T) {r&#43;1, R, i});
		while(R &gt; r) {q[i].ans -= pref[R-1]; --R;}
	}
	memset(t, 0, sizeof t);
	for(int l, r, id, i = 1; i &lt;= n; &#43;&#43;i) {
		for(int j = 0; j &lt; buc.size(); &#43;&#43;j) &#43;&#43;t[a[i]^buc[j]];
		for(int o = 0; o &lt; v[i].size(); &#43;&#43;o) {
			l = v[i][o].l; r = v[i][o].r; id = v[i][o].id;
			for(int j = l, tmp = 0; j &lt;= r; &#43;&#43;j) {
				tmp = t[a[j]];
				if(j &lt;= i &amp;&amp; !k) --tmp;
				if(id &gt; 0) q[id].ans &#43;= tmp;
				else q[-id].ans -= tmp;
			}
		}
	}
	for(int i = 1; i &lt;= m; &#43;&#43;i) q[i].ans &#43;= q[i-1].ans;
	for(int i = 1; i &lt;= m; &#43;&#43;i) ans[q[i].id] = q[i].ans;
	for(int i = 1; i &lt;= m; &#43;&#43;i) printf(&#34;%lld\n&#34;, ans[i]);
}
```

## 莫比乌斯反演

```C&#43;&#43;
void GetMu() {
	mu[1] = 1;
	for(int i = 2; i &lt;= 10000000; &#43;&#43;i) {
		if(!vis[i]) p[&#43;&#43;cnt] = i, mu[i] = -1;
		for(int j = 1; j &lt;= cnt &amp;&amp; p[j] * i &lt;= 10000000; &#43;&#43;j) {
			vis[p[j]*i] = 1;
			if(i % p[j]) mu[p[j]*i] = -mu[i];
		}
	}
	for(int i = 1; i &lt;= cnt; &#43;&#43;i)
		for(int j = 1; j * p[i] &lt;= 10000000; &#43;&#43;j)
			f[j*p[i]] &#43;= mu[j];
	for(int i = 1; i &lt;= 10000000; &#43;&#43;i) pref[i] = pref[i-1] &#43; f[i];
}
lint calc(int a, int b) {
	lint res = 0;
	if(a &gt; b) swap(a, b);
	for(int l = 1, r = 0; l &lt;= a; l = r &#43; 1) {
		r = min(a/(a/l), b/(b/l));
		res &#43;= (pref[r] - pref[l-1])*1ll*(a/l)*(b/l);
	} return res;
}
```

## 树剖

```c&#43;&#43;
void ADD(int u, int l, int r, int k) {t[u] = (t[u] &#43; 1ll*k*(r-l&#43;1)%P) % P; tag[u] = (tag[u] &#43; k) % P;}
void PD(int u, int l, int r) {ADD(L(u), l, mid, tag[u]); ADD(R(u), mid&#43;1, r, tag[u]); tag[u] = 0;}
void PU(int u) {t[u] = (t[L(u)] &#43; t[R(u)]) % P;}
void build(int u, int l, int r) {
	if(l == r) {t[u] = w[id[l]]; return; }
	build(L(u), l, mid); build(R(u), mid&#43;1, r); PU(u); 
}
void upd(int u, int l, int r, int tl, int tr, int k) {
	if(tr &lt; l || tl &gt; r) return; if(tl &lt;= l &amp;&amp; r &lt;= tr) ADD(u, l, r, k);
	else PD(u, l, r), upd(L(u), l, mid, tl, tr, k), upd(R(u), mid&#43;1, r, tl, tr, k), PU(u);
}
int qry(int u, int l, int r, int tl, int tr) {
	if(tr &lt; l || tl &gt; r) return 0; if(tl &lt;= l &amp;&amp; r &lt;= tr) return t[u]; PD(u, l, r);
	return (qry(L(u), l, mid, tl, tr) &#43; qry(R(u), mid&#43;1, r, tl, tr)) % P;
}
void dfs1(int u, int p) {
	fa[u] = p; siz[u] = 1; dep[u] = dep[p] &#43; 1;
	for(int v, i = h[u]; ~i; i = e[i].next)
		if((v = e[i].to) != p) {
			dfs1(v, u); siz[u] &#43;= siz[v];
			if(siz[son[u]] &lt; siz[v]) son[u] = v;
		}
}
void dfs2(int u, int p) {
	id[dfn[u] = &#43;&#43;idx] = u; top[u] = p;
	if(son[u]) dfs2(son[u], p);
	for(int v, i = h[u]; ~i; i = e[i].next)
		if((v = e[i].to) != fa[u] &amp;&amp; v != son[u]) dfs2(v, v);
}
void addpath(int x, int y, int k) {
	for(; top[x] != top[y]; x = fa[top[x]]) {
		if(dep[top[x]] &lt; dep[top[y]]) swap(x, y);
		upd(1, 1, n, dfn[top[x]], dfn[x], k);
	}
	if(dep[x] &gt; dep[y]) swap(x, y);
	upd(1, 1, n, dfn[x], dfn[y], k);
}
int qrypath(int x, int y) {
	int res = 0;
	for(; top[x] != top[y]; x = fa[top[x]]) {
		if(dep[top[x]] &lt; dep[top[y]]) swap(x, y);
		res = (res &#43; qry(1, 1, n, dfn[top[x]], dfn[x])) % P;
	}
	if(dep[x] &gt; dep[y]) swap(x, y);
	return (res &#43; qry(1, 1, n, dfn[x], dfn[y])) % P;
}
void addroot(int x, int k) {upd(1, 1, n, dfn[x], dfn[x] &#43; siz[x] - 1, k); }
int qryroot(int x) {return qry(1, 1, n, dfn[x], dfn[x] &#43; siz[x] - 1);}
```

## 主席树

```c&#43;&#43;
struct JZM_T {int ch[2], v;} t[MAXN &lt;&lt; 6];
int cnt, rt[MAXN &lt;&lt; 6], o[MAXN], a[MAXN], n, m;
void build(int &amp;u, int l, int r) {
	t[u = &#43;&#43;cnt].v = 0;
	if(l != r) build(L(u), l, mid), build(R(u), mid&#43;1, r);
}
void update(int &amp;u, int v, int l, int r, int p, int k) {
	t[u = &#43;&#43;cnt] = t[v]; t[u].v &#43;= k;
	if(l != r) p &lt;= mid ? update(L(u), L(v), l, mid, p, k) : update(R(u), R(v), mid&#43;1, r, p, k);
}
int query(int tl, int tr, int l, int r, int k) {
	if(l == r) return o[l]; int s = t[L(tr)].v - t[L(tl)].v;
	return k &lt;= s ? query(L(tl), L(tr), l, mid, k) : query(R(tl), R(tr), mid&#43;1, r, k-s);
}
int main() {
	read(n); read(m);
	for(int i = 1; i &lt;= n; &#43;&#43;i) read(a[i]), o[i] = a[i];
	sort(o&#43;1, o&#43;n&#43;1); int _n = unique(o&#43;1, o&#43;n&#43;1)-o-1; build(rt[0], 1, _n);
	for(int i = 1; i &lt;= n; &#43;&#43;i)
		update(rt[i], rt[i-1], 1, _n, lower_bound(o&#43;1, o&#43;_n&#43;1, a[i])-o, 1);
	for(int l, r, k; m--; ) {
		read(l); read(r); read(k);
		printf(&#34;%d\n&#34;, query(rt[l-1], rt[r], 1, _n, k));
	}
}
```

## GCD-BlackMagic

```C&#43;&#43;
int gcd(int a, int b) {
	int g = 1;
	for(int tmp, i = 0; i &lt; 3; b /= tmp, g *= tmp, &#43;&#43;i)
		tmp = (k[a][i] &gt; siz) ? (b % k[a][i] == 0 ? k[a][i] : 1) : _gcd[k[a][i]][b%k[a][i]];
	return g;
}
int main() {
	k[1][0] = k[1][1] = k[1][2] = 1; notp[1] = 1;
	for(int i = 2; i &lt;= V; &#43;&#43;i) {
		if(!notp[i]) p[&#43;&#43;cnt] = i, k[i][2] = i, k[i][1] = k[i][0] = 1;
		for(int j = 1; p[j] * i &lt;= V; &#43;&#43;j) {
			notp[i * p[j]] = 1; int *t = k[i*p[j]];
			t[0] = k[i][0] * p[j]; t[1] = k[i][1]; t[2] = k[i][2];
			if(t[1] &lt; t[0]) swap(t[0], t[1]); if(t[2] &lt; t[1]) swap(t[1], t[2]);
			if(i % p[j] == 0) break;
		}
	}
	for(int i = 1; i &lt;= siz; &#43;&#43;i) _gcd[i][0] = _gcd[0][i] = i;
	for(int _max = 1; _max &lt;= siz; &#43;&#43;_max)
		for(int i = 1; i &lt;= _max; &#43;&#43;i)
			_gcd[i][_max] = _gcd[_max][i] = _gcd[_max % i][i];
```

## FFT

```C&#43;&#43;
struct Complex {
	double x, y;
	Complex(double xx = 0, double yy = 0) {x = xx; y = yy;}
	Complex operator &#43; (Complex &amp;b) const {return Complex(x&#43;b.x, y&#43;b.y);}
	Complex operator - (Complex &amp;b) const {return Complex(x-b.x, y-b.y);}
	Complex operator * (Complex &amp;b) const {return Complex(x*b.x-y*b.y, y*b.x&#43;x*b.y);}
} a[MAXN], b[MAXN];
int r[MAXN], n, m, l, limit;
void FFT (Complex *A, int t) {
	for(int i = 0; i &lt; limit; &#43;&#43;i)
		if(i &lt; r[i]) swap(A[i], A[r[i]]);
	for(int mid = 1; mid &lt; limit; mid &lt;&lt;= 1) {
		Complex Wn = Complex(cos(Pi/mid), t * sin(Pi/mid));
		for(int R = mid&lt;&lt;1, j = 0; j &lt; limit; j &#43;= R) {
			Complex w = Complex(1, 0);
			for(int k = 0; k &lt; mid; &#43;&#43;k, w = w * Wn) {
				Complex x = A[j&#43;k], y = w*A[j&#43;mid&#43;k];
				A[j&#43;k] = x&#43;y; A[j&#43;mid&#43;k] = x-y;
			}
		}
	}
}
int main() {
	n = read(); m = read();
	for(int i = 0; i &lt;= n; &#43;&#43;i) a[i].x = read();
	for(int i = 0; i &lt;= m; &#43;&#43;i) b[i].x = read();
	for(limit = 1; limit &lt;= n&#43;m; limit &lt;&lt;= 1, &#43;&#43;l);
	for(int i = 0; i &lt; limit; &#43;&#43;i) r[i] = (r[i&gt;&gt;1]&gt;&gt;1)|((i&amp;1)&lt;&lt;(l-1));
	FFT(a, 1); FFT(b, 1);
	for(int i = 0; i &lt;= limit; &#43;&#43;i) a[i] = a[i]*b[i];
	FFT(a, -1);
	for(int i = 0; i &lt;= n&#43;m; &#43;&#43;i) printf(&#34;%d &#34;, (int)(a[i].x/limit&#43;0.5));
	puts(&#34;&#34;);
	
} 
```

## 多项式

```c&#43;&#43;
#include&lt;bits/stdc&#43;&#43;.h&gt;
#define ll long long
#define FIO &#34;loj150&#34;
using namespace std;
const int N=1e5&#43;5,MOD=998244353,P=19,INV2=MOD&#43;1&gt;&gt;1;

inline int add(int a,const int &amp;b){if((a&#43;=b)&gt;=MOD)a-=MOD;return a;}
inline int sub(int a,const int &amp;b){if((a-=b)&lt;		0)a&#43;=MOD;return a;}
inline int mul(const int &amp;a,const int &amp;b){return 1ll*a*b%MOD;}
inline void inc(int &amp;a,const int &amp;b=1){a=add(a,b);}
inline void dec(int &amp;a,const int &amp;b=1){a=sub(a,b);}
inline void pro(int &amp;a,const int &amp;b){a=mul(a,b);}
inline int qpow(int a,int b){int c=1;for(;b;b&gt;&gt;=1,pro(a,a))if(b&amp;1)pro(c,a);return c;}

int n,k,w[2][1&lt;&lt;P];

inline void pre(){
	for(int i=1;i&lt;1&lt;&lt;P;i&lt;&lt;=1){
		w[0][i]=w[1][i]=1;
		int wn1=qpow(3,(MOD-1)/(i&lt;&lt;1)),wn0=qpow(wn1,MOD-2);
		for(int j=1;j&lt;i;j&#43;&#43;)
			w[0][i&#43;j]=mul(w[0][i&#43;j-1],wn0),w[1][i&#43;j]=mul(w[1][i&#43;j-1],wn1);
	}
}

#define poly vector&lt;int&gt; 
inline void read(poly &amp;a,const int &amp;n){
	a.resize(n);
	for(int i=0;i&lt;n;i&#43;&#43;)scanf(&#34;%d&#34;,&amp;a[i]);
}

inline void out(const poly &amp;a){
	for(int i=0,n=a.size();i&lt;n;i&#43;&#43;)printf(&#34;%d%c&#34;,a[i],i^n-1?&#39; &#39;:&#39;\n&#39;);
}

inline void clear(poly &amp;a){
	int n=a.size();
	while(n&gt;1&amp;&amp;!a[n-1])n--;
	a.resize(n);
}

inline poly operator &#43;(poly a,const int &amp;b){inc(a[0],b);return a;}
inline poly operator &#43;(const int &amp;b,poly a){inc(a[0],b);return a;}
inline poly operator -(poly a,const int &amp;b){dec(a[0],b);return a;}
inline poly operator -(const int &amp;b,poly a){dec(a[0],b);return a;}

inline poly operator &#43;(poly a,const poly &amp;b){
	if(a.size()&lt;b.size())a.resize(b.size());
	for(int i=0,n=a.size();i&lt;n;i&#43;&#43;)inc(a[i],b[i]);
	return a;
}

inline poly operator -(poly a,const poly &amp;b){
	if(a.size()&lt;b.size())a.resize(b.size());
	for(int i=0,n=a.size();i&lt;n;i&#43;&#43;)dec(a[i],b[i]);
	return a;
}

inline void ntt(int *f,int opt,int l){
	poly rev(l);
	for(int i=0;i&lt;l;i&#43;&#43;){rev[i]=(rev[i&gt;&gt;1]&gt;&gt;1)|((i&amp;1)*(l&gt;&gt;1));if(i&lt;rev[i])swap(f[i],f[rev[i]]);}
	for(int i=1;i&lt;l;i&lt;&lt;=1)
		for(int j=0;j&lt;l;j&#43;=i&lt;&lt;1)
			for(int k=0;k&lt;i;k&#43;&#43;){
				int x=f[j&#43;k],y=mul(f[i&#43;j&#43;k],w[opt][i&#43;k]);
				f[j&#43;k]=add(x,y);
				f[i&#43;j&#43;k]=sub(x,y);
			}
	if(opt)for(int i=0,inv=qpow(l,MOD-2);i&lt;l;i&#43;&#43;)pro(f[i],inv);
}

inline poly operator *(poly a,poly b){
	int n=a.size(),m=b.size(),l=1;
	while(l&lt;n&#43;m)l&lt;&lt;=1;
	a.resize(l);b.resize(l);
	ntt(&amp;a[0],0,l);ntt(&amp;b[0],0,l);
	for(int i=0;i&lt;l;i&#43;&#43;)pro(a[i],b[i]);
	ntt(&amp;a[0],1,l);
	clear(a);
	return a;
}

inline poly&amp; operator *=(poly &amp;a,const poly b){return a=a*b;}

inline poly operator *(poly a,const int &amp;b){
	for(int i=0,n=a.size();i&lt;n;i&#43;&#43;)pro(a[i],b);
	return a;
}

inline poly inv(const poly &amp;a,const int &amp;n){
	if(n==1)return poly(1,qpow(a[0],MOD-2));
	int l=1;while(l&lt;=n&lt;&lt;1)l&lt;&lt;=1;
	poly b=inv(a,n&#43;1&gt;&gt;1),c(l);b.resize(l);
	for(int i=0;i&lt;n;i&#43;&#43;)c[i]=a[i];
	ntt(&amp;b[0],0,l);ntt(&amp;c[0],0,l);
	for(int i=0;i&lt;l;i&#43;&#43;)pro(b[i],sub(2,mul(b[i],c[i])));
	ntt(&amp;b[0],1,l);
	b.resize(n);
	clear(b);
	return b;
}

inline poly inv(const poly &amp;a){return inv(a,a.size());}

int B;
#define pii pair&lt;int,int&gt;
inline pii operator *(pii a,pii b){
	return pii(add(mul(a.first,b.first),mul(mul(a.second,b.second),B)),add(mul(a.first,b.second),mul(a.second,b.first)));
}
inline pii qpow(pii a,int b){pii c=pii(1,0);for(;b;b&gt;&gt;=1,a=a*a)if(b&amp;1)c=c*a;return c;}

inline int remain(int x){
	if(x&lt;=1)return x;
	int a=mul(mul(rand(),rand()),rand());
	while(qpow(B=sub(mul(a,a),x),MOD-1&gt;&gt;1)==1)a=mul(mul(rand(),rand()),rand());
	pii A=pii(a,1),ans=qpow(A,MOD&#43;1&gt;&gt;1);
	return min(ans.first,MOD-ans.first);
}

inline poly sqrt(const poly &amp;a,const int &amp;n){
	if(n==1)return poly(1,remain(a[0]));
	int l=1;while(l&lt;=n&lt;&lt;1)l&lt;&lt;=1;
	poly b=sqrt(a,n&#43;1&gt;&gt;1),c(l),d;
	b.resize(n);d=inv(b)*INV2;
	b.resize(l);d.resize(l);
	for(int i=0;i&lt;n;i&#43;&#43;)c[i]=a[i];
	ntt(&amp;b[0],0,l);ntt(&amp;c[0],0,l);ntt(&amp;d[0],0,l);
	for(int i=0;i&lt;l;i&#43;&#43;)b[i]=mul(d[i],add(mul(b[i],b[i]),c[i]));
	ntt(&amp;b[0],1,l);
	b.resize(n);
	clear(b);
	return b;
}

inline poly sqrt(const poly &amp;a){return sqrt(a,a.size());}

inline poly deri(poly a){
	int n=a.size();
	if(n==1)return poly(1,0);
	for(int i=0;i&lt;n;i&#43;&#43;)a[i]=mul(a[i&#43;1],i&#43;1);
	a.resize(n-1);
	return a;
}

inline poly inte(poly a){
	int n=a.size();
	a.resize(n&#43;1);
	for(int i=n;i;i--)a[i]=mul(a[i-1],qpow(i,MOD-2));
	a[0]=0;
	return a;
}

inline poly ln(const poly &amp;a){
	int n=a.size();
	poly c=inv(a)*deri(a);
	c.resize(n-1);
	return inte(c);
}

inline poly exp(const poly &amp;a,const int &amp;n){
	if(n==1)return poly(1,1);
	poly b=exp(a,n&#43;1&gt;&gt;1),c;
	b.resize(n);c=ln(b);
	for(int i=0;i&lt;n;i&#43;&#43;)c[i]=sub(a[i],c[i]);
	inc(c[0]);
	b*=c;
	b.resize(n);
	return b;
}

inline poly exp(const poly &amp;a){return exp(a,a.size());}

inline poly qpow(poly a,const double &amp;b){return exp(ln(a)*b);}

poly a;

int main(){
	srand(19260817);
	pre();

	scanf(&#34;%d%d&#34;,&amp;n,&amp;k);
	read(a,1&#43;n);
	a=deri(qpow(1&#43;ln(2&#43;a-a[0]-exp(inte(inv(sqrt(a))))),k));
	a.resize(n);
	out(a);
	return 0;
}
```

## 珂朵莉树

```c&#43;&#43;
//以防我忘了set迭代器怎么写
struct node {
	int l, r;
	mutable lint v;
	node(int L, int R = -1, lint V = 0) : l(L), r(R), v(V) {}
	bool operator &lt; (const node &amp;o) const {
		return l &lt; o.l;
	}
};
set &lt;node&gt; s;
IT spilit (int pos) {
	IT it = s.lower_bound(node(pos));
	if(it != s.end() &amp;&amp; it-&gt;l == pos) return it;
	it--;
	int L = it -&gt; l, R = it -&gt; r;
	lint V = it-&gt;v;
	s.erase(it);
	s.insert(node(L, pos-1, V));
	return s.insert(node(pos, R, V)).first;
}
void add(int l, int r, int val) {
	IT il = spilit(l), ir = spilit(r&#43;1);
	for(; il != ir; il-&gt;v &#43;= val, il&#43;&#43;);
}
void tp(int l, int r, int val = 0) {
	IT il = spilit(l), ir = spilit(r&#43;1);
	s.erase(il, ir);
	s.insert(node(l, r, val));
}
```



---

> Author: Shino  
> URL: https://www.sh1no.icu/posts/templates/  

