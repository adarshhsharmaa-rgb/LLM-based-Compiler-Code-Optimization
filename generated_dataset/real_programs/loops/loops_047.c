// category: loops  (real program 047)
// Codeforces submission 18213021, problem 301/C, GNU C++, 2016-06-02
// https://codeforces.com/contest/301/submission/18213021
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
using namespace std;
int main()
 {
    for (int i=0;i<9;i++)
      printf("%d??<>%d\n",i,i+1);
    puts("9??>>??0\n??<>1");
    for (int i=0;i<10;i++)
      printf("?%d>>%d?\n",i,i);
    puts("?>>??\n>>?");
 }
