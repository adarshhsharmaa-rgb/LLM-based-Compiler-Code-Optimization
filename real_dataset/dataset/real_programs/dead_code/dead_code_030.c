// category: dead_code  (real program 030)
// Codeforces submission 45291742, problem 1075/A, GNU C++11, 2018-11-04
// https://codeforces.com/contest/1075/submission/45291742
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

int main(){
    long long n,x,y;
    scanf("%I64d%I64d%I64d", &n,&x,&y);
    int m=n;
    if(x==n && y==n) printf("Black");
    else if(x==1 && y==1) printf("White");
    else if(((x-1)+(y-1))<((n-x)+(n-y))) printf("White");
    else if(((x-1)+(y-1))>((n-x)+(n-y))) printf("Black");
    else if(((x-1)+(y-1))==((n-x)+(n-y))) printf("White");
return 0;
}
