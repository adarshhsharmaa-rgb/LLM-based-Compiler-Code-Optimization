// category: arithmetic  (real program 017)
// Codeforces submission 18339309, problem 669/A, GNU C++11, 2016-06-09
// https://codeforces.com/contest/669/submission/18339309
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h> 

using namespace std;



int n;



int main(){

	scanf("%d", &n);

	int cnt = n / 3;

	int rem = n % 3;

	printf("%d\n", cnt*2 + (rem > 0));

	return 0;

}
