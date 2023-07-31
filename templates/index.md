# 板子 (ver.诗乃)


## Tarjan&Topo

```C++
void tarjan(int u) {
	dfn[u] = low[u] = ++tim; ins[u] = 1; stac[++top] = u;
	for(int v, i = h[u]; ~i; i = e[i].next)
		if(!dfn[(v = e[i].to)]) {
			tarjan(v);
			low[u] = min(low[u], low[v]);
		} else if(ins[v]) low[u] = min(low[u], low[v]);
	if(low[u] == dfn[u]) {
		int y; while(y = stac[top--]) {
            sd[y] = u; ins[y] = 0; if(u == y) break; p[u] += p[y];
        }
	}
}
void topo() {
	queue <int> q;
	for(int i = 1; i <= n; ++i)
		if(sd[i] == i && !in[i]) q.push(i), dis[i] = p[i];
	while(!q.empty()) {
		int u = q.front(); q.pop();
		for(int v, i = h[u]; ~i; i = e[i].next) {
				v = e[i].to;
				dis[v] = max(dis[v], dis[u] + p[v]);
				--in[v]; if(!in[v]) q.push(v);
			}
	}
	int ans = 0;
	for(int i = 1; i <= n; ++i) ans = max(ans, dis[i]);
	printf("%d\n", ans);
}
```

## ST

```C++
void ST_Build() {
	for(int j = 1; j <= 21; ++j)
		for(int i = 1; i + (1 << j) - 1 <= n; ++i)
			st[i][j] = max(st[i][j-1], st[i+(1<<(j-1))][j-1]);
}
int ST_query(int l, int r) {
	int k = lg2[r-l+1];
	return max(st[l][k], st[r-(1<<k)+1][k]);
}
```

## ST-BlackMagic

```c++
struct RMQ {
	#define L(x) ((x-1)*siz+1)
	#define R(x) std::min(n, x*siz+1)
	#define bl(x) ((x-1)/siz+1)
	const int MAXB = 2050, siz = 50;
	int prf[MAXN], suf[MAXN], n, st[MAXB][13], lg2[MAXN], a[MAXN];
	void init(int *s, int _n, int k) {
		n = _n;
		for(int i = 1; i <= n; ++i)
            a[i] = s[i] % k, st[bl(i)][0] = min(st[bl(i)][0], a[i]);
		for(int i = 1; i <= bl(n); ++i) {
			prf[L(i)] = a[L(i)]; suf[R(i)] = a[R(i)];
			for(int j = L(i)+1; j <= R(i); ++j) prf[j] = min(prf[j-1], a[j]);
			for(int j = R(i)-1; j >= L(i); --j) suf[j] = min(suf[j+1], a[j]);
		}
		for(int j = 1; j <= 12; ++j)
			for(int i = 1; i + (1 << j) - 1 <= bl(n); ++i)
				st[i][j] = min(st[i][j-1], st[i+(1<<(j-1))][j-1]);
	}
	int QST(int l, int r) {
		if(l > r) return 0; int k = lg2[r-l+1];
		return min(st[l][k], st[r-(1<<k)+1][k]);
	}
	int query(int l, int r) {
		if(bl(l) == bl(r)) {
			int res = 0;
			for(int i = l; i <= r; ++i) res = max(res, a[i]);
			return res;
		} else return min(min(prf[r], suf[l]), QST(bl(l)+1, bl(r)-1));
	}
} ST;
```

## Manacher

```c++
void Manacher() {
	int mr = 0, mid;
	for(int i = 0; i < n; ++i) {
		p[i] = i < mr ? min(p[(mid << 1) - i], p[mid] + mid - i) : 1;
		for(; s[i-p[i]] == s[i+p[i]]; ++p[i]);
		if(p[i] + i > mr) mr = i + p[i], mid = i;
	}
}
int main() {
	scanf("%s", a); _n = strlen(a);
	s[0] = s[1] = '#'; n = 1;
	for(int i = 0; i < _n; ++i) s[++n] = a[i], s[++n] = '#';
	s[++n] = 0; Manacher();
	for(int i = 0; i < n; ++i) ans = max(ans, p[i]);
	printf("%d\n", ans-1);
}
```

## 线性基

```C++
for(int i = 1; i <= n; ++i) {
		read(a);
		for(int j = 50; j >= 0; --j) {
			if((a >> j) & 1) {
				if(!p[j]) {p[j] = a; break;}
				a ^= p[j];
			}
		}
	}
	for(int i = 50; i >= 0; --i)
		if(p[i]) ans = max(ans, ans ^ p[i]);
```

## 线性逆元

```c++
inv[1] = 1;
for(int i = 2; i <= n; ++i)
	inv[i] = 1ll * (P - P / i) % P * inv[P % i]	% P;
```

## 后缀数组

```C++
void getSA() {
	for(int i = 1; i <= n; ++i) ++c[x[i] = s[i]];
	for(int i = 1; i <= m; ++i) c[i] += c[i-1];
	for(int i = n; i >= 1; --i) sa[c[x[i]]--] = i;
	for(int k = 1; k <= n; k <<= 1) {
		int num = 0;
		for(int i = n - k + 1; i <= n; ++i) y[++num] = i;
		for(int i = 1; i <= n; ++i) if(sa[i] > k) y[++num] = sa[i] - k;
		memset(c, 0, sizeof c);
		for(int i = 1; i <= n; ++i) ++c[x[i]];
		for(int i = 1; i <= m; ++i) c[i] += c[i-1];
		for(int i = n; i >= 1; --i) sa[c[x[y[i]]]--] = y[i], y[i] = 0;
		swap(x, y);
		x[sa[1]] = 1; num = 0;
		for(int i = 1; i <= n; ++i)
			x[sa[i]] = (y[sa[i-1]] == y[sa[i]] && y[sa[i-1]+k] == y[sa[i]+k]) ? num : ++num;
		if(num == n) break;
		m = num;
	}
}
```

## 点分治

```C++
void getroot(int u, int p, int S) {
	siz[u] = 1, f[u] = 0;
	for(int v, i = h[u]; ~i; i = e[i].next)
		if((v = e[i].to) != p && !vis[v])
			getroot(v, u, S), siz[u] += siz[v], f[u] = max(f[u], siz[v]);
	f[u] = max(f[u], S - siz[u]); rt = f[u] < f[rt] ? u : rt;
}
void getdis(int u, int p) {
	stk[++top] = dis[u];
	for(int v, i = h[u]; ~i; i = e[i].next)
		if((v = e[i].to) != p && !vis[v])
			dis[v] = dis[u] + e[i].w, getdis(v, u);
}
void solve(int u, int w, int t) {
	top = 0, dis[u] = w, getdis(u, 0);
	for(int i = 1; i <= top; ++i)
		for(int j = 1; j <= top; ++j)
			if(i != j) ans[stk[i] + stk[j]] += t;
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

```C++
#define L(u) (u<<1)
#define R(u) (u<<1|1)
#define mid ((l+r)>>1)
void PU(int u) {t[u] = (t[L(u)] + t[R(u)]) % P;}
void ADD(int u, int l, int r, int k) {
	t[u] += (r - l + 1) * k % P; t[u] %= P; add[u] = (add[u] + k) % P;
}
void MUL(int u, int l, int r, int k) {
	t[u] = t[u] * k % P; add[u] = add[u] * k % P; mul[u] = mul[u] * k % P;
}
void PD(int u, int l, int r) {
	MUL(L(u), l, mid, mul[u]); MUL(R(u), mid+1, r, mul[u]); mul[u] = 1;
	ADD(L(u), l, mid, add[u]); ADD(R(u), mid+1, r, add[u]); add[u] = 0;
}
void build(int u, int l, int r) {
	mul[u] = 1; if(l == r) {t[u] = a[l]; return;}
	build(L(u), l, mid); build(R(u), mid+1, r); PU(u);
}
void MA(int u, int l, int r, int tl, int tr, int k) {
	if(tr < l || tl > r) return;
	if(tl <= l && r <= tr) {ADD(u, l, r, k); return;}
	PD(u, l, r); MA(L(u), l, mid, tl, tr, k); MA(R(u), mid+1, r, tl, tr, k); PU(u);
}
void MM(int u, int l, int r, int tl, int tr, int k) {
	if(tr < l || tl > r) return;
	if(tl <= l && r <= tr) {MUL(u, l, r, k); return;}
	PD(u, l, r); MM(L(u), l, mid, tl, tr, k); MM(R(u), mid+1, r, tl, tr, k); PU(u);
}
int Q(int u, int l, int r, int tl, int tr) {
	if(tr < l || tl > r) return 0; if(tl <= l && r <= tr) return t[u];
	PD(u, l, r); return (Q(L(u), l, mid, tl, tr) + Q(R(u), mid+1, r, tl, tr)) % P;
}
```

## 三分

```C++
while(fabs(r-l) >= eps) {
	double mid = (l + r) / 2;
	if(f(mid - eps) < f(mid + eps)) l = mid;
	else r = mid;
}
```

## 树状数组

```c++
void U(int x, int k) {for(; x <= n; t[x] += k, x += x&-x);}
int Q(int x) {int w = 0; for(; x; w += t[x], x -= x&-x); return w;}
```

## 高斯消元

```C++
for(int i = 1; i <= n; ++i) {
	int p = i;
	for(int j = i + 1; j <= n; ++j)
		if(fabs(a[j][i]) > fabs(a[p][i])) p = j;
	if(a[p][i] == 0) {puts("No Solution"); return 0;}
	for(int j = 1; j <= n+1; ++j) swap(a[i][j], a[p][j]);
	for(int j = 1; j <= n; ++j) {
		if(i == j) continue;
		double t = a[j][i] / a[i][i];
		for(int k = i; k <= n+1; ++k) a[j][k] -= a[i][k] * t;
	}
}
for(int i = 1; i <= n; ++i) printf("%.2lf\n", a[i][n+1] / a[i][i]);
```

## 最小生成树&并查集

```C++
int findfa(int x) {return x == fa[x] ? x : fa[x] = findfa(fa[x]);}
int main() {
	for(int i = 1; i <= n; ++i) fa[i] = i;
	sort(e+1, e+m+1);
	for(int i = 1; i <= m; ++i) {
		int x = findfa(e[i].u), y = findfa(e[i].v);
		if(x == y) continue;
		ans += e[i].w; ++cnt;
		if(cnt == n-1) break;
		fa[x] = y;
	}
}
```

## DINIC

```C++
bool bfs() {
	memset(d, -1, sizeof d); queue <int> q; q.push(s); d[s] = 0;
	while(!q.empty()) {
		int u = q.front(); q.pop();
		for(int v, i = h[u]; ~i; i = e[i].next)
			if(d[v = e[i].to] == -1 && e[i].w > 0)
				d[v] = d[u] + 1, q.push(v);
	}
	return d[t] != -1;
}
int dfs(int u, int f) {
	int r = 0;
	if(u == t) return f;
	for(int v, i = h[u]; ~i && r < f; i = e[i].next)
		if(d[(v = e[i].to)] == d[u] + 1 && e[i].w > 0) {
			int x = dfs(v, min(e[i].w, f-r));
			e[i].w -= x; e[i^1].w += x; r += x;
		}
	if(!r) d[u] = -1; return r;
}
int dinic() {
	int x, ans = 0;
	while(bfs()) while(x = dfs(s, 1e9)) ans += x;
	return ans;
}
```

## 线性筛

```C++
for(int i = 2; i <= n; ++i) {
	if(!notp[i]) p[++cntp] = i;
	for(int j = 1; 1ll*i*p[j] <= n && j <= cntp; ++j) {
		notp[i*p[j]] = 1;
		if(i % p[j] == 0) break;
	}
}
```

## 左偏树

```C++
int F(int x) {return x == fa[x] ? x : fa[x] = F(fa[x]);}
int Merge(int x, int y) {
	if(x*y == 0) return x+y;
	if(v[x] > v[y] || (v[x] == v[y] && x > y)) swap(x, y);
	R(x) = Merge(R(x), y); fa[R(x)] = fa[L(x)] = x;
	if(dis[R(x)] > dis[L(x)]) swap(L(x), R(x));
	dis[x] = dis[R(x)] + 1; return x;
}
int Top(int x) {return del[x] ? -1 : v[x];}
void Pop(int x) {
	if(del[x]) return; del[x] = 1;
	fa[L(x)] = L(x); fa[R(x)] = R(x);
	fa[x] = Merge(L(x), R(x));
}
```

## LCT

```c++
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
	int y = x, z = 0; st[++z] = y;
	while(nroot(y)) st[++z] = y = fa[y]; while(z) pushdown(st[z--]);
	for(int y; nroot(x); rotate(x)) if(nroot(y = fa[x])) rotate((y == ch[fa[y]][0]) ^ (x == ch[y][0]) ? x : y);
	pushup(x);
}
void access(int x) {for(int y = 0; x; x = fa[y = x]) splay(x), ch[x][1] = y, pushup(x);}
void makeroot(int x) {access(x); splay(x); pushr(x);}
int findroot(int x) {access(x); splay(x); for(; ch[x][0]; x = ch[x][0]) pushdown(x); splay(x); return x;}
void spilit(int x, int y) {makeroot(x); access(y); splay(y);}
void link(int x, int y) {makeroot(x); if(findroot(y) != x) fa[x] = y;}
void cut(int x, int y) {makeroot(x); if(findroot(y) == x && fa[y] == x && !ch[y][0]) {fa[y] = ch[x][1] = 0; pushup(x);}}
```

## KMP

```C++
for(int i = 2, j = 0; i <= n; ++i) {
	while(j && s[i] != s[j+1]) j = nxt[j];
	if(s[j+1] == s[i]) ++j; nxt[i] = j;
}
for(int i = 1, j = 0; i <= m; ++i) {
	while(j > 0 && t[i] != s[j+1]) j = nxt[j];
	if(s[j+1] == t[i]) ++j;
	if(j == n) printf("%d\n", i-n+1);
}
```

## SAM

```C++
struct SoumAsuMire {
	int ch[MAXN][26], fa[MAXN], last, cnt, len[MAXN];
	void insert(int c) {
		int p = last, np = ++cnt; last = np; len[np] = len[p] + 1;
		for(; p && !ch[p][c]; ch[p][c] = np, p = fa[p]);
		if(!p) fa[np] = 1;
		else {
			int q = ch[p][c];
			if(len[q] == len[p] + 1) fa[np] = q;
			else {
				int nq = ++cnt; len[nq] = len[p] + 1;
				memcpy(ch[nq], ch[q], sizeof ch[q]);
				fa[nq] = fa[q]; fa[q] = fa[np] = nq;
				for(; p && ch[p][c] == q; ch[p][c] = nq, p = fa[p]);
			}
		}
	}
	void build(char *s) {
		int n = strlen(s+1); last = 1;
		for(int i = 1; i <= n; ++i) insert(s[i] - 'a');
	}
	int getans() {
		int ans = 0;
		for(int i = 2; i <= cnt; ++i) ans += len[i] - len[fa[i]];
		return ans;
	}
} SAM;
```

## LCA(ST)

```C++
void dfsRMQ(int u, int p) {
	st[++idx][0] = u; dfn[u] = idx; dep[u] = dep[p] + 1;
	for(int v, i = h[u]; ~i; i = e[i].next)
		if((v = e[i].to) != p) dfsRMQ(v, u), st[++idx][0] = u;
}
void LCAinit() {
	for(int i = 2; i <= (n << 1); ++i) lg2[i] = lg2[i>>1] + 1;
	dep[1] = 1; dfsRMQ(rt, 0);
	for(int j = 1; j < 20; ++j)
		for(int i = 1; i + (1 << j) <= (n << 1); ++i)
			st[i][j] = Min(st[i][j-1], st[i+(1<<(j-1))][j-1]);
}
int LCA(int x, int y) {
	x = dfn[x]; y = dfn[y];
	if(x > y) swap(x, y);
	int k = lg2[y-x+1];
	return Min(st[x][k], st[y-(1<<k)+1][k]);
}
```

## mcmf

```C++
bool SPFA() {
	memset(d, 63, sizeof d); memset(vis, 0, sizeof vis); memset(flow, 63, sizeof flow);
	queue <int> q; q.push(s); d[s] = 0; vis[s] = 1;
	while(!q.empty()) {
		int u = q.front(); q.pop(); vis[u] = 0;
		for(int v, i = h[u]; ~i; i = e[i].next)
			if(d[v = e[i].to] > d[u] + e[i].c && e[i].f) {
				d[v] = d[u] + e[i].c; pos[v] = i;
				fa[v] = u; flow[v] = min(flow[u], e[i].f);
				if(!vis[v]) vis[v] = 1, q.push(v);
			}
	} return flow[s] != flow[t];
}
void mcmf() {
	while(SPFA()) {
		mc += flow[t]; mf += flow[t] * d[t];
		for(int u = t; u != s; u = fa[u]) e[pos[u]].f -= flow[t], e[pos[u]^1].f += flow[t];
	}
}
```

## AC自动机

```c++
#include <bits/stdc++.h>
using namespace std;
const int S = 2000050, T = 200050;
struct Edge {int to, next;} e[T];
char s[S]; int n, h[T], cnt, ch[T][26], fail[T], match[T], siz[T], tot = 1, en;
queue <int> q;
void addedge(int u, int v) {e[en] = (Edge) {v, h[u]}; h[u] = en++;}
void dfs(int u) {
	for(int v, i = h[u]; ~i; i = e[i].next)
		dfs(v = e[i].to), siz[u] += siz[v];
}
int main() {
	scanf("%d", &n); memset(h, -1, sizeof h);
	for(int i = 1; i <= n; ++i) {
		scanf("%s", s); int u = 1, j;
		for(u = 1, j = 0; s[j]; ++j) {
			int c = s[j] - 'a';
			if(!ch[u][c]) ch[u][c] = ++tot;
			u = ch[u][c];
		} match[i] = u;
	}
	for(int i = 0; i < 26; ++i) ch[0][i] = 1;
	q.push(1);
	while(!q.empty()) {
		int u = q.front(); q.pop();
		for(int i = 0; i < 26; ++i) 
			if(ch[u][i]) {
				fail[ch[u][i]] = ch[fail[u]][i];
				q.push(ch[u][i]);
			} else ch[u][i] = ch[fail[u]][i];
	}
	scanf("%s", s);
	for(int u = 1, i = 0; s[i]; ++i) ++siz[u = ch[u][s[i]-'a']];
	for(int i = 2; i <= tot; ++i) addedge(fail[i], i); dfs(1);
	for(int i = 1; i <= n; ++i) printf("%d\n", siz[match[i]]);
	puts("");
}
```

## dijkstra

```C++
void dijkstra() {
	memset(d, 0x3f, sizeof d);
	d[s] = 0; q.push((D) {s, 0});
	while(!q.empty()) {
		int u = q.top().u; q.pop();
		if(vis[u]) continue; vis[u] = 1;
		for(int v, i = h[u]; ~i; i = e[i].next)
			if(d[v = e[i].to] > d[u] + e[i].w) {
				d[v] = d[u] + e[i].w;
				if(!vis[v]) q.push((D) {v, d[v]});
			}
	}
}
```

## 树哈希

```C++
ull Hash(int u, int p) {
	ull q[MAXN], ans = X; int top = 0;
	for(int i = h[u]; ~i; i = e[i].next)
		if(e[i].to != p) q[++top] = Hash(e[i].to, u);
	sort(q+1, q+top+1);
	for(int i = 1; i <= top; ++i) ans = ans * P + q[i];
	return ans * P + X + 1;
}
```

## CDQ分治

```c++
struct BITS {
	int t[MAXN];
	void U(int x, int k) {for(; x <= m; t[x] += k, x += x&-x);}
	int Q(int x) {int res = 0; for(; x; res += t[x], x -= x&-x); return res;}
} T;
void cdq(int l, int r) {
	if(l == r) return; int mid = (l + r) >> 1;
	cdq(l, mid); cdq(mid+1, r);
	sort(a+l, a+mid+1, cmpy); sort(a+mid+1, a+r+1, cmpy);
	int i = mid + 1, j = l;
	for(; i <= r; ++i) {
		for(; a[j].y <= a[i].y && j <= mid; ++j) T.U(a[j].z, a[j].w);
		a[i].ans += T.Q(a[i].z);
	} for(int k = l; k < j; ++k) T.U(a[k].z, -a[k].w);
}
int main() {
	read(_n); read(m);
	for(int i = 1; i <= _n; ++i) read(b[i].x), read(b[i].y), read(b[i].z);
	sort(b+1, b+_n+1, cmpx);
	for(int c = 0, i = 1; i <= _n; ++i) {
		++c;
		if(b[i].x != b[i+1].x || b[i].y != b[i+1].y || b[i].z != b[i+1].z)
			a[++n] = b[i], a[n].w = c, c = 0;
	} cdq(1, n);
	for(int i = 1; i <= n; ++i) cnt[a[i].ans + a[i].w - 1] += a[i].w;
	for(int i = 0; i < _n; ++i) printf("%d\n", cnt[i]);
}
```

## Lucas

```C++
int C(int n, int m) {
	if(m > n) return 0;
	return 1ll * fac[n] * power(fac[m], P-2) * power(fac[n-m], P-2);
}
int Lucas(int n, int m) {
	if(m == 0) return 1;
	return 1ll * C(n%P, m%P) * Lucas(n/P, m/P) % P;
}
```

## 二分图

```c++
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

```c++
#include <bits/stdc++.h>
using namespace std;
const int MAXN = 100050;
typedef long long lint;
void read(int &x) {
	char ch; while(ch = getchar(), ch < '!'); x = ch - 48;
	while(ch = getchar(), ch > '!') x = (x << 3) + (x << 1) + ch - 48;
}
struct Qry {int l, r, id; lint ans;} q[MAXN];
struct T{int l, r, id;};
int n, m, a[MAXN], siz[MAXN], k, blsz, bl[MAXN], t[MAXN], pref[MAXN];
vector <int> buc; vector <T> v[MAXN]; lint ans[MAXN];
int cmp(Qry a, Qry b) {return bl[a.l] == bl[b.l] ? a.r < b.r : a.l < b.l;}
int main() {
	read(n); read(m); read(k); blsz = sqrt(n);
	if(k > 14) {for(int i = 1; i <= m; ++i) puts("0"); return 0;}
	for(int i = 1; i <= n; ++i) read(a[i]);
	for(int i = 0; i < 16384; ++i) if((siz[i] = siz[(i>>1)] + (i&1)) == k) buc.push_back(i);
	for(int i = 1; i <= m; ++i) read(q[i].l), read(q[i].r), q[i].id = i;
	for(int i = 1; i <= n; ++i) bl[i] = (i-1) / blsz + 1;
	sort(q+1, q+m+1, cmp);
	for(int i = 1; i <= n; ++i) {
		for(int j = 0; j < buc.size(); ++j) ++t[a[i]^buc[j]];
		pref[i] = t[a[i+1]];
	}
	for(int L = 1, R = 0, i = 1; i <= m; ++i) {
		int l = q[i].l, r = q[i].r;
		   if(L < l) v[R].push_back((T) {L, l-1, -i});
		while(L < l) {q[i].ans += pref[L-1]; ++L;}
		   if(L > l) v[R].push_back((T) {l, L-1, i});
		while(L > l) {q[i].ans -= pref[L-2]; --L;}
		   if(R < r) v[L-1].push_back((T) {R+1, r, -i});
		while(R < r) {q[i].ans += pref[R]; ++R;}
		   if(R > r) v[L-1].push_back((T) {r+1, R, i});
		while(R > r) {q[i].ans -= pref[R-1]; --R;}
	}
	memset(t, 0, sizeof t);
	for(int l, r, id, i = 1; i <= n; ++i) {
		for(int j = 0; j < buc.size(); ++j) ++t[a[i]^buc[j]];
		for(int o = 0; o < v[i].size(); ++o) {
			l = v[i][o].l; r = v[i][o].r; id = v[i][o].id;
			for(int j = l, tmp = 0; j <= r; ++j) {
				tmp = t[a[j]];
				if(j <= i && !k) --tmp;
				if(id > 0) q[id].ans += tmp;
				else q[-id].ans -= tmp;
			}
		}
	}
	for(int i = 1; i <= m; ++i) q[i].ans += q[i-1].ans;
	for(int i = 1; i <= m; ++i) ans[q[i].id] = q[i].ans;
	for(int i = 1; i <= m; ++i) printf("%lld\n", ans[i]);
}
```

## 莫比乌斯反演

```C++
void GetMu() {
	mu[1] = 1;
	for(int i = 2; i <= 10000000; ++i) {
		if(!vis[i]) p[++cnt] = i, mu[i] = -1;
		for(int j = 1; j <= cnt && p[j] * i <= 10000000; ++j) {
			vis[p[j]*i] = 1;
			if(i % p[j]) mu[p[j]*i] = -mu[i];
		}
	}
	for(int i = 1; i <= cnt; ++i)
		for(int j = 1; j * p[i] <= 10000000; ++j)
			f[j*p[i]] += mu[j];
	for(int i = 1; i <= 10000000; ++i) pref[i] = pref[i-1] + f[i];
}
lint calc(int a, int b) {
	lint res = 0;
	if(a > b) swap(a, b);
	for(int l = 1, r = 0; l <= a; l = r + 1) {
		r = min(a/(a/l), b/(b/l));
		res += (pref[r] - pref[l-1])*1ll*(a/l)*(b/l);
	} return res;
}
```

## 树剖

```c++
void ADD(int u, int l, int r, int k) {t[u] = (t[u] + 1ll*k*(r-l+1)%P) % P; tag[u] = (tag[u] + k) % P;}
void PD(int u, int l, int r) {ADD(L(u), l, mid, tag[u]); ADD(R(u), mid+1, r, tag[u]); tag[u] = 0;}
void PU(int u) {t[u] = (t[L(u)] + t[R(u)]) % P;}
void build(int u, int l, int r) {
	if(l == r) {t[u] = w[id[l]]; return; }
	build(L(u), l, mid); build(R(u), mid+1, r); PU(u); 
}
void upd(int u, int l, int r, int tl, int tr, int k) {
	if(tr < l || tl > r) return; if(tl <= l && r <= tr) ADD(u, l, r, k);
	else PD(u, l, r), upd(L(u), l, mid, tl, tr, k), upd(R(u), mid+1, r, tl, tr, k), PU(u);
}
int qry(int u, int l, int r, int tl, int tr) {
	if(tr < l || tl > r) return 0; if(tl <= l && r <= tr) return t[u]; PD(u, l, r);
	return (qry(L(u), l, mid, tl, tr) + qry(R(u), mid+1, r, tl, tr)) % P;
}
void dfs1(int u, int p) {
	fa[u] = p; siz[u] = 1; dep[u] = dep[p] + 1;
	for(int v, i = h[u]; ~i; i = e[i].next)
		if((v = e[i].to) != p) {
			dfs1(v, u); siz[u] += siz[v];
			if(siz[son[u]] < siz[v]) son[u] = v;
		}
}
void dfs2(int u, int p) {
	id[dfn[u] = ++idx] = u; top[u] = p;
	if(son[u]) dfs2(son[u], p);
	for(int v, i = h[u]; ~i; i = e[i].next)
		if((v = e[i].to) != fa[u] && v != son[u]) dfs2(v, v);
}
void addpath(int x, int y, int k) {
	for(; top[x] != top[y]; x = fa[top[x]]) {
		if(dep[top[x]] < dep[top[y]]) swap(x, y);
		upd(1, 1, n, dfn[top[x]], dfn[x], k);
	}
	if(dep[x] > dep[y]) swap(x, y);
	upd(1, 1, n, dfn[x], dfn[y], k);
}
int qrypath(int x, int y) {
	int res = 0;
	for(; top[x] != top[y]; x = fa[top[x]]) {
		if(dep[top[x]] < dep[top[y]]) swap(x, y);
		res = (res + qry(1, 1, n, dfn[top[x]], dfn[x])) % P;
	}
	if(dep[x] > dep[y]) swap(x, y);
	return (res + qry(1, 1, n, dfn[x], dfn[y])) % P;
}
void addroot(int x, int k) {upd(1, 1, n, dfn[x], dfn[x] + siz[x] - 1, k); }
int qryroot(int x) {return qry(1, 1, n, dfn[x], dfn[x] + siz[x] - 1);}
```

## 主席树

```c++
struct JZM_T {int ch[2], v;} t[MAXN << 6];
int cnt, rt[MAXN << 6], o[MAXN], a[MAXN], n, m;
void build(int &u, int l, int r) {
	t[u = ++cnt].v = 0;
	if(l != r) build(L(u), l, mid), build(R(u), mid+1, r);
}
void update(int &u, int v, int l, int r, int p, int k) {
	t[u = ++cnt] = t[v]; t[u].v += k;
	if(l != r) p <= mid ? update(L(u), L(v), l, mid, p, k) : update(R(u), R(v), mid+1, r, p, k);
}
int query(int tl, int tr, int l, int r, int k) {
	if(l == r) return o[l]; int s = t[L(tr)].v - t[L(tl)].v;
	return k <= s ? query(L(tl), L(tr), l, mid, k) : query(R(tl), R(tr), mid+1, r, k-s);
}
int main() {
	read(n); read(m);
	for(int i = 1; i <= n; ++i) read(a[i]), o[i] = a[i];
	sort(o+1, o+n+1); int _n = unique(o+1, o+n+1)-o-1; build(rt[0], 1, _n);
	for(int i = 1; i <= n; ++i)
		update(rt[i], rt[i-1], 1, _n, lower_bound(o+1, o+_n+1, a[i])-o, 1);
	for(int l, r, k; m--; ) {
		read(l); read(r); read(k);
		printf("%d\n", query(rt[l-1], rt[r], 1, _n, k));
	}
}
```

## GCD-BlackMagic

```C++
int gcd(int a, int b) {
	int g = 1;
	for(int tmp, i = 0; i < 3; b /= tmp, g *= tmp, ++i)
		tmp = (k[a][i] > siz) ? (b % k[a][i] == 0 ? k[a][i] : 1) : _gcd[k[a][i]][b%k[a][i]];
	return g;
}
int main() {
	k[1][0] = k[1][1] = k[1][2] = 1; notp[1] = 1;
	for(int i = 2; i <= V; ++i) {
		if(!notp[i]) p[++cnt] = i, k[i][2] = i, k[i][1] = k[i][0] = 1;
		for(int j = 1; p[j] * i <= V; ++j) {
			notp[i * p[j]] = 1; int *t = k[i*p[j]];
			t[0] = k[i][0] * p[j]; t[1] = k[i][1]; t[2] = k[i][2];
			if(t[1] < t[0]) swap(t[0], t[1]); if(t[2] < t[1]) swap(t[1], t[2]);
			if(i % p[j] == 0) break;
		}
	}
	for(int i = 1; i <= siz; ++i) _gcd[i][0] = _gcd[0][i] = i;
	for(int _max = 1; _max <= siz; ++_max)
		for(int i = 1; i <= _max; ++i)
			_gcd[i][_max] = _gcd[_max][i] = _gcd[_max % i][i];
```

## FFT

```C++
struct Complex {
	double x, y;
	Complex(double xx = 0, double yy = 0) {x = xx; y = yy;}
	Complex operator + (Complex &b) const {return Complex(x+b.x, y+b.y);}
	Complex operator - (Complex &b) const {return Complex(x-b.x, y-b.y);}
	Complex operator * (Complex &b) const {return Complex(x*b.x-y*b.y, y*b.x+x*b.y);}
} a[MAXN], b[MAXN];
int r[MAXN], n, m, l, limit;
void FFT (Complex *A, int t) {
	for(int i = 0; i < limit; ++i)
		if(i < r[i]) swap(A[i], A[r[i]]);
	for(int mid = 1; mid < limit; mid <<= 1) {
		Complex Wn = Complex(cos(Pi/mid), t * sin(Pi/mid));
		for(int R = mid<<1, j = 0; j < limit; j += R) {
			Complex w = Complex(1, 0);
			for(int k = 0; k < mid; ++k, w = w * Wn) {
				Complex x = A[j+k], y = w*A[j+mid+k];
				A[j+k] = x+y; A[j+mid+k] = x-y;
			}
		}
	}
}
int main() {
	n = read(); m = read();
	for(int i = 0; i <= n; ++i) a[i].x = read();
	for(int i = 0; i <= m; ++i) b[i].x = read();
	for(limit = 1; limit <= n+m; limit <<= 1, ++l);
	for(int i = 0; i < limit; ++i) r[i] = (r[i>>1]>>1)|((i&1)<<(l-1));
	FFT(a, 1); FFT(b, 1);
	for(int i = 0; i <= limit; ++i) a[i] = a[i]*b[i];
	FFT(a, -1);
	for(int i = 0; i <= n+m; ++i) printf("%d ", (int)(a[i].x/limit+0.5));
	puts("");
	
} 
```

## 多项式

```c++
#include<bits/stdc++.h>
#define ll long long
#define FIO "loj150"
using namespace std;
const int N=1e5+5,MOD=998244353,P=19,INV2=MOD+1>>1;

inline int add(int a,const int &b){if((a+=b)>=MOD)a-=MOD;return a;}
inline int sub(int a,const int &b){if((a-=b)<		0)a+=MOD;return a;}
inline int mul(const int &a,const int &b){return 1ll*a*b%MOD;}
inline void inc(int &a,const int &b=1){a=add(a,b);}
inline void dec(int &a,const int &b=1){a=sub(a,b);}
inline void pro(int &a,const int &b){a=mul(a,b);}
inline int qpow(int a,int b){int c=1;for(;b;b>>=1,pro(a,a))if(b&1)pro(c,a);return c;}

int n,k,w[2][1<<P];

inline void pre(){
	for(int i=1;i<1<<P;i<<=1){
		w[0][i]=w[1][i]=1;
		int wn1=qpow(3,(MOD-1)/(i<<1)),wn0=qpow(wn1,MOD-2);
		for(int j=1;j<i;j++)
			w[0][i+j]=mul(w[0][i+j-1],wn0),w[1][i+j]=mul(w[1][i+j-1],wn1);
	}
}

#define poly vector<int> 
inline void read(poly &a,const int &n){
	a.resize(n);
	for(int i=0;i<n;i++)scanf("%d",&a[i]);
}

inline void out(const poly &a){
	for(int i=0,n=a.size();i<n;i++)printf("%d%c",a[i],i^n-1?' ':'\n');
}

inline void clear(poly &a){
	int n=a.size();
	while(n>1&&!a[n-1])n--;
	a.resize(n);
}

inline poly operator +(poly a,const int &b){inc(a[0],b);return a;}
inline poly operator +(const int &b,poly a){inc(a[0],b);return a;}
inline poly operator -(poly a,const int &b){dec(a[0],b);return a;}
inline poly operator -(const int &b,poly a){dec(a[0],b);return a;}

inline poly operator +(poly a,const poly &b){
	if(a.size()<b.size())a.resize(b.size());
	for(int i=0,n=a.size();i<n;i++)inc(a[i],b[i]);
	return a;
}

inline poly operator -(poly a,const poly &b){
	if(a.size()<b.size())a.resize(b.size());
	for(int i=0,n=a.size();i<n;i++)dec(a[i],b[i]);
	return a;
}

inline void ntt(int *f,int opt,int l){
	poly rev(l);
	for(int i=0;i<l;i++){rev[i]=(rev[i>>1]>>1)|((i&1)*(l>>1));if(i<rev[i])swap(f[i],f[rev[i]]);}
	for(int i=1;i<l;i<<=1)
		for(int j=0;j<l;j+=i<<1)
			for(int k=0;k<i;k++){
				int x=f[j+k],y=mul(f[i+j+k],w[opt][i+k]);
				f[j+k]=add(x,y);
				f[i+j+k]=sub(x,y);
			}
	if(opt)for(int i=0,inv=qpow(l,MOD-2);i<l;i++)pro(f[i],inv);
}

inline poly operator *(poly a,poly b){
	int n=a.size(),m=b.size(),l=1;
	while(l<n+m)l<<=1;
	a.resize(l);b.resize(l);
	ntt(&a[0],0,l);ntt(&b[0],0,l);
	for(int i=0;i<l;i++)pro(a[i],b[i]);
	ntt(&a[0],1,l);
	clear(a);
	return a;
}

inline poly& operator *=(poly &a,const poly b){return a=a*b;}

inline poly operator *(poly a,const int &b){
	for(int i=0,n=a.size();i<n;i++)pro(a[i],b);
	return a;
}

inline poly inv(const poly &a,const int &n){
	if(n==1)return poly(1,qpow(a[0],MOD-2));
	int l=1;while(l<=n<<1)l<<=1;
	poly b=inv(a,n+1>>1),c(l);b.resize(l);
	for(int i=0;i<n;i++)c[i]=a[i];
	ntt(&b[0],0,l);ntt(&c[0],0,l);
	for(int i=0;i<l;i++)pro(b[i],sub(2,mul(b[i],c[i])));
	ntt(&b[0],1,l);
	b.resize(n);
	clear(b);
	return b;
}

inline poly inv(const poly &a){return inv(a,a.size());}

int B;
#define pii pair<int,int>
inline pii operator *(pii a,pii b){
	return pii(add(mul(a.first,b.first),mul(mul(a.second,b.second),B)),add(mul(a.first,b.second),mul(a.second,b.first)));
}
inline pii qpow(pii a,int b){pii c=pii(1,0);for(;b;b>>=1,a=a*a)if(b&1)c=c*a;return c;}

inline int remain(int x){
	if(x<=1)return x;
	int a=mul(mul(rand(),rand()),rand());
	while(qpow(B=sub(mul(a,a),x),MOD-1>>1)==1)a=mul(mul(rand(),rand()),rand());
	pii A=pii(a,1),ans=qpow(A,MOD+1>>1);
	return min(ans.first,MOD-ans.first);
}

inline poly sqrt(const poly &a,const int &n){
	if(n==1)return poly(1,remain(a[0]));
	int l=1;while(l<=n<<1)l<<=1;
	poly b=sqrt(a,n+1>>1),c(l),d;
	b.resize(n);d=inv(b)*INV2;
	b.resize(l);d.resize(l);
	for(int i=0;i<n;i++)c[i]=a[i];
	ntt(&b[0],0,l);ntt(&c[0],0,l);ntt(&d[0],0,l);
	for(int i=0;i<l;i++)b[i]=mul(d[i],add(mul(b[i],b[i]),c[i]));
	ntt(&b[0],1,l);
	b.resize(n);
	clear(b);
	return b;
}

inline poly sqrt(const poly &a){return sqrt(a,a.size());}

inline poly deri(poly a){
	int n=a.size();
	if(n==1)return poly(1,0);
	for(int i=0;i<n;i++)a[i]=mul(a[i+1],i+1);
	a.resize(n-1);
	return a;
}

inline poly inte(poly a){
	int n=a.size();
	a.resize(n+1);
	for(int i=n;i;i--)a[i]=mul(a[i-1],qpow(i,MOD-2));
	a[0]=0;
	return a;
}

inline poly ln(const poly &a){
	int n=a.size();
	poly c=inv(a)*deri(a);
	c.resize(n-1);
	return inte(c);
}

inline poly exp(const poly &a,const int &n){
	if(n==1)return poly(1,1);
	poly b=exp(a,n+1>>1),c;
	b.resize(n);c=ln(b);
	for(int i=0;i<n;i++)c[i]=sub(a[i],c[i]);
	inc(c[0]);
	b*=c;
	b.resize(n);
	return b;
}

inline poly exp(const poly &a){return exp(a,a.size());}

inline poly qpow(poly a,const double &b){return exp(ln(a)*b);}

poly a;

int main(){
	srand(19260817);
	pre();

	scanf("%d%d",&n,&k);
	read(a,1+n);
	a=deri(qpow(1+ln(2+a-a[0]-exp(inte(inv(sqrt(a))))),k));
	a.resize(n);
	out(a);
	return 0;
}
```

## 珂朵莉树

```c++
//以防我忘了set迭代器怎么写
struct node {
	int l, r;
	mutable lint v;
	node(int L, int R = -1, lint V = 0) : l(L), r(R), v(V) {}
	bool operator < (const node &o) const {
		return l < o.l;
	}
};
set <node> s;
IT spilit (int pos) {
	IT it = s.lower_bound(node(pos));
	if(it != s.end() && it->l == pos) return it;
	it--;
	int L = it -> l, R = it -> r;
	lint V = it->v;
	s.erase(it);
	s.insert(node(L, pos-1, V));
	return s.insert(node(pos, R, V)).first;
}
void add(int l, int r, int val) {
	IT il = spilit(l), ir = spilit(r+1);
	for(; il != ir; il->v += val, il++);
}
void tp(int l, int r, int val = 0) {
	IT il = spilit(l), ir = spilit(r+1);
	s.erase(il, ir);
	s.insert(node(l, r, val));
}
```


