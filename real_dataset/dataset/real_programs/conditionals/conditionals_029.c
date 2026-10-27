// category: conditionals  (real program 029)
// Codeforces submission 14699041, problem 206/D1, GNU C++, 2015-12-08
// https://codeforces.com/contest/206/submission/14699041
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
int main(){
    int m; scanf("%d",&m);
    if(m>=54000)printf("1");
    else if (m <= 50000)printf("3");
    else printf("2");
}
