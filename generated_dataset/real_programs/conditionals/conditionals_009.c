// category: conditionals  (real program 009)
// Codeforces submission 192737742, problem 652/A, C++20 (GCC 11-64), 2023-02-08
// https://codeforces.com/contest/652/submission/192737742
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>


int main(){
int h1, h2, a, b;
scanf("%d %d\n%d %d", &h1, &h2, &a, &b);

h2 -= h1 + 8 * a;
a = (a - b) * 12;

if(h2 <= 0){puts("0");}
else if(a <= 0){puts("-1");}
else{printf("%d\n",(h2 + a - 1) / a);}

return 0;
}
