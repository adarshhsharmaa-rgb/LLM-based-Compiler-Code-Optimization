// category: conditionals  (real program 017)
// Codeforces submission 37611009, problem 965/A, C++17 (GCC 7-32), 2018-04-25
// https://codeforces.com/contest/965/submission/37611009
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
int main() {
    int k,n,s,p;
    scanf("%d%d%d%d",&k,&n,&s,&p);
    long long int a,b,c;
    a = n/s;
    if(n % s != 0)
        a = a + 1;
    b = k * a;
    c = b/p;
    if(b % p != 0)
        c = c + 1;
    printf("%lld",c);
}
