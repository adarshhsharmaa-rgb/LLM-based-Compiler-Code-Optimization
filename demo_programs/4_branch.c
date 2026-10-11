#include <stdio.h>

/* A decision that depends on the user's input. */
int main() {
    int marks;
    scanf("%d", &marks);

    int bonus = 3 + 2;
    int grade = 0;
    if (marks >= 40) {
        grade = marks * 1 + bonus;
    } else if (marks >= 30) {
        grade = marks + 0;
    } else {
        grade = 0 * marks;
    }
    printf("%d\n", grade);
    return 0;
}
