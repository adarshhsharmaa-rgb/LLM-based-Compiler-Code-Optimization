// category: conditionals  (real program 067)
// Codeforces submission 519245, problem 93/A, GNU C++, 2011-06-30
// https://codeforces.com/contest/93/submission/519245
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int     n,m,a,b,fx,fy,ex,ey;

int main(){
    scanf("%d%d%d%d",&n,&m,&a,&b);
    
    fx=(a-1)/m+1;
    fy=a%m;
    if (!fy)    fy=m;
    ex=(b-1)/m+1;
    ey=b%m;
    if (!ey)    ey=m;
    if (b==n)   ey=m;
    if (fx==ex || (fy==1 && ey==m))
        printf("1\n");
    else{
        if (fx+1==ex || fy==1 || ey+1==fy || ey==m)
            printf("2\n");
        else
            printf("3\n");
    }
    
    return 0;
}
