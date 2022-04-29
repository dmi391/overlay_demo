/**
 * @file demo_class.cpp
 * @author PehotinDO
 */

#include "demo_class.h"

int32_t DemoClass::series[] = {0, 1, 1, 2, 3, 5, 8};	///< Static field. To .data section


/**
 * @brief Calculate specific Fibbonachi value
 *
 * @param[in] val Order number
 * @return Fibbonachi value
 *
 */
uint32_t DemoClass::getFibonacciVal(uint32_t n)
{
	uint32_t prevprev = DemoClass::series[0];
	uint32_t prev = DemoClass::series[1];
	uint32_t curr = 0;

	if(n <= 1)
	{
		return(DemoClass::series[n]);
	}
	for(uint32_t i = 1; i < n; i++)
	{
		curr = prevprev + prev;
		//for next cycle:
		prevprev = prev;
		prev = curr;
	}
	return(curr);
}


/**
 * @brief Find index of max element in array of integer
 *
 * @param[in] len Lenght of array
 * @param[in] src Array of integer
 * @return Index of max element
 *
 */
uint32_t DemoClass::findIndexMaxElement(uint32_t len, int32_t* src)
{
	uint32_t indexMax = 0;
	uint32_t max = src[0];

	for(uint32_t i = 0; i < len; i++)
	{
		if(src[i] >= max)
		{
			max = src[i];
			indexMax = i;
		}
	}
	return indexMax;
}
