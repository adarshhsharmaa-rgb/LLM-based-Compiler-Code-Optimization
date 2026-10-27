// category: loops  (real program 012)
// Codeforces submission 17853234, problem 672/A, GNU C, 2016-05-11
// https://codeforces.com/contest/672/submission/17853234
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

int main(){
  //freopen("f.in", "r", stdin);
  //freopen("f.out", "w", stdout);
  int n, i, p10, ci, last;
  scanf("%d", &n);
  for(i = 1; n > 0; i++){
    ci = i;
    p10 = 1;
    while(p10 <= ci)
      p10 *= 10;
    p10 /= 10;
    while(n > 0 && p10 > 0){
      last = ci / p10;
      ci %= p10;
      p10 /= 10;
      n--;
    }
  }
  printf("%d", last);
  return 0;
}
