// category: loops  (real program 064)
// Codeforces submission 21302193, problem 327/B, C++14 (GCC 6-32), 2016-10-08
// https://codeforces.com/contest/327/submission/21302193
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>



int main(){

    long n; scanf("%ld\n", &n);

    for(long k = n + 1; k <= 2 * n; k++){printf("%ld ", k);}

    printf("\n");

    return 0;

}
