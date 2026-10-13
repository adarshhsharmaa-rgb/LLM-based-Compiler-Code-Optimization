// category: loops  (real program 073)
// Codeforces submission 21800443, problem 732/A, GNU C++, 2016-10-26
// https://codeforces.com/contest/732/submission/21800443
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

#define pb push_back

#define mp make_pair

#define VI vector<int>

#define pii pair<int,int>

#define matrix vector<VI>

#define LL long long

#define INF 0x3f3f3f3f

#define ULL unsigned long long

#define MOD 1000000007

#define uedge(g,a,b) g[a].pb(b), g[b].pb(a)

#define dedge(g,a,b) g[a].pb(b)

using namespace std;

int n, m;

int main(){

	scanf("%d %d", &n, &m);

	int p = n, s = 1;

	while(!(p%10 == 0 || ((p/10)*10 + m) == p)){

		s++;

		p += n;

	}

	printf("%d\n", s);

	return 0;

}
