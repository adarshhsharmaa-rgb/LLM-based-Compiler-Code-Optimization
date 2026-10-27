// category: repeated_expr  (real program 041)
// Codeforces submission 21509727, problem 476/D, C++14 (GCC 6-32), 2016-10-17
// https://codeforces.com/contest/476/submission/21509727
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>

using namespace std;



int main(){

    int n, k;

    scanf("%d %d", &n, &k);

    printf("%d\n", (6*n-1)*k);

    for(int i = 0; i < n; i++)

        printf("%d %d %d %d\n", (6*i+1)*k, (6*i+2)*k, (6*i+3)*k, (6*i+5)*k);

    return 0;

}
