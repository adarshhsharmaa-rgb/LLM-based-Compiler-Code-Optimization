// category: mixed  (real program 012)
// Codeforces submission 22138673, problem 579/A, GNU C++11, 2016-11-09
// https://codeforces.com/contest/579/submission/22138673
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>



using namespace std;



int main()

{

    int cnts = 0;

    int n;

    scanf("%d", &n);

    while(n != 0){

        int x = n % 2;

        if(x == 1) cnts++;

        n = n / 2;

    }

    printf("%d", cnts);

}
