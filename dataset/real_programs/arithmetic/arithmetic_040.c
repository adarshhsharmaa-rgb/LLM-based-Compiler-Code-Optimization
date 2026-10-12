// category: arithmetic  (real program 040)
// Codeforces submission 6537894, problem 125/A, GNU C++, 2014-05-03
// https://codeforces.com/contest/125/submission/6537894
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <cmath>
int main(){
    int c;
    scanf("%d",&c);
    c=(c+1)/3;
    printf("%d %d\n",c/12,c%12);
   return 0;
}
