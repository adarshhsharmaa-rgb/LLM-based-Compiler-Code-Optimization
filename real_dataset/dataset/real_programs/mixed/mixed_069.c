// category: mixed  (real program 069)
// Codeforces submission 3956660, problem 306/A, GNU C++, 2013-06-24
// https://codeforces.com/contest/306/submission/3956660
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
int n,m,i;
int main (){
    scanf("%d %d",&n,&m);
    for (i=0;i<m;i++){
        if (i>0) printf(" ");
        printf("%d",(n+i)/m);
    }
    return 0;
}
