/**
 * @file main.cpp
 * @author PehotinDO
 */
#include <cmath>


#include <cstdint>

#include "demo_class.h"
#include "ovlymgr.h"

int foobar (int);


int main()
{
	bool isErr = true;

	OverlayLoad(0);
	//Call function from overlay
	int32_t a = foobar(1);

	OverlayLoad(1);
	//Call static methods from overlay
	uint32_t fibVal = DemoClass::getFibonacciVal(8);
	uint32_t indexMax = DemoClass::findIndexMaxElement(7, DemoClass::series);

	if(a == ('f' + 'o' +'o' + 'b' + 'a' + 'r') &&
	(fibVal == 21) && (indexMax == 6))
	{
		isErr = false;
	}

	return isErr;
}
