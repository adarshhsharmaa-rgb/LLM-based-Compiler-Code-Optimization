// category: dead_code  (real program 058)
// Codeforces submission 16925586, problem 652/A, GNU C++, 2016-03-25
// https://codeforces.com/contest/652/submission/16925586
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
//day = 10 am
//night = 10 pm
//start at 2 pm

#include "stdio.h"

int main(){
	int h1,h2;
		scanf("%d %d",&h1,&h2);
	int a,b;
		scanf("%d %d",&a,&b);
		
	unsigned long long int hour = 0;
	int firstUp = a*8;
	int up = a*12;
	int down = b*12;
	int sumDay = up - down;
	
	if(h1 + firstUp >= h2){
		printf("0");
		return 0;
	}
		
	if(sumDay <= 0){
		printf("-1");
		return 0;
	}

	h1 += firstUp;
	//go to 10 pm
	
	int days = (h2 - h1)/sumDay + ((h2-h1)%sumDay > 0);
	h1 += ((h2 - h1)/sumDay)*sumDay;
	
	printf("%d",days);
	
	return 0;
}
