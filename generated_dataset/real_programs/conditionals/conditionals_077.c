// category: conditionals  (real program 077)
// Codeforces submission 20810228, problem 472/A, C++14 (GCC 6-32), 2016-09-22
// https://codeforces.com/contest/472/submission/20810228
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
#define pb push_back
#define mp make_pair
#define fst first
#define snd second
#define fore(i,a,b) for(int i=a,to=b;i<to;++i)
using namespace std;

typedef long long ll;

int main(){
	int n;
	scanf("%d",&n);
	if(n%2)printf("%d %d\n",9,n-9);
	else printf("%d %d\n",4,n-4);
	return 0;
}
