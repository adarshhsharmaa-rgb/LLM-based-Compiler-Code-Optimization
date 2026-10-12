// category: mixed  (real program 002)
// Codeforces submission 7073988, problem 320/A, GNU C++, 2014-07-13
// https://codeforces.com/contest/320/submission/7073988
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
int main(){
    int n;
    scanf("%d",&n);
    while(n>0){
         if(n%10!=1&&n%100!=14&&n%1000!=144){
            printf("NO");
            return 0;
         }
         n/=10;
    }
    printf("YES");
    return 0;
}
