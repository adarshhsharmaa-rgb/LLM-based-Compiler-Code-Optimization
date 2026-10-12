// category: repeated_expr  (real program 039)
// Codeforces submission 521325, problem 93/A, GNU C++, 2011-06-30
// https://codeforces.com/contest/93/submission/521325
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int n,m,a,b;
int main(){
    int wai,waj,wbi,wbj;
    scanf("%d%d%d%d",&n,&m,&a,&b);
    if (a%m>0) {
        wai=a/m+1;
        waj=a%m;
    }
    else {
        wai=a/m;
        waj=m;
    }
    if (b%m>0){
        wbi=b/m+1;
        wbj=b%m;
    }
    else{
        wbi=b/m;
        wbj=m;
    }
    if (waj==1&&b==n) printf("1\n");
    else if (wai==wbi) printf("1\n");
    else if (waj==1&&wbj==m) printf("1\n");
    else if (wbj==m) printf("2\n");
    else if (wbi-wai==1) printf("2\n");
    else if (waj==1) printf("2\n");
    else if (wbj==waj-1) printf("2\n");
    else if (b==n) printf("2\n");
    else printf("3\n");
    return 0;
}
