// category: repeated_expr  (real program 029)
// Codeforces submission 20833545, problem 622/A, C++14 (GCC 6-32), 2016-09-23
// https://codeforces.com/contest/622/submission/20833545
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>







int main()

{

   long long in,num;

   num=1;

   scanf("%I64d",&in);

   for (num=1;(num*(num+1))/2<in;num++);

   //printf("%d\n",num);

   num=num-1;

   printf("%I64d\n",in-(num*(num+1))/2);





    return 0;

}
