// category: repeated_expr  (real program 048)
// Codeforces submission 21556323, problem 492/A, GNU C++11, 2016-10-18
// https://codeforces.com/contest/492/submission/21556323
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>



using namespace std;



int main()

{

    int n;

    scanf("%d", &n);

    int sum = 0;

    int i = 1;

    while(sum + (i * (i + 1) / 2) <= n){

        sum += i * (i + 1) / 2;

        i++;

    }

    printf("%d", i - 1);

    return 0;

}
