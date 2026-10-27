// category: dead_code  (real program 020)
// Codeforces submission 20358641, problem 610/A, GNU C++, 2016-09-03
// https://codeforces.com/contest/610/submission/20358641
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;

int main()

{

    int i, j, k, n, m, t, p, cas=1;

    scanf("%d", &n);

    if(n%2==1) printf("0\n");

    else if(n%4==0) printf("%d\n", (n/4)-1);

    else if(n%4!=0) printf("%d\n", (n/4));

    return 0;

}
