// category: conditionals  (real program 051)
// Codeforces submission 22173067, problem 65/A, C++14 (GCC 6-32), 2016-11-12
// https://codeforces.com/contest/65/submission/22173067
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>

int n,a,b,c,d,e,f;

int main()

{

	scanf("%d%d%d%d%d%d",&a,&b,&c,&d,&e,&f);

	if (d==0) {puts("Hermione"); return 0;}

	if (c==0) {puts("Ron"); return 0;}

	if (b==0) {puts("Hermione"); return 0;}

	if (a==0) {puts("Ron"); return 0;}

	if (f==0) {puts("Hermione"); return 0;}

	if (e==0) {puts("Ron"); return 0;}

	if (b*d*f>a*c*e) puts("Ron");

	else puts("Hermione");

}
