// category: dead_code  (real program 037)
// Codeforces submission 16886227, problem 320/A, GNU C++, 2016-03-23
// https://codeforces.com/contest/320/submission/16886227
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
main(){
    int i=0,j,s=0,n;
    scanf("%d",&n);
    while(n)
    {
        if(n%10!=1 && n%100!=14 && n%1000!=144) 
        s=1;
    n/=10;
    }
    if(!s)  puts("YES");
    else puts("NO");
    return 0;
}
