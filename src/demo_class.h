/**
 * @file demo_class.h
 * @author PehotinDO
 */

#ifndef DEMO_CLASS_H_
#define DEMO_CLASS_H_

#include <cstdint>

/**
 * @brief Demo example class
 *
 */
class DemoClass
{
	public:
		DemoClass() {};
		~DemoClass() {};

		static int32_t series[];	//to .data section

		static uint32_t getFibonacciVal(uint32_t n);
		static uint32_t findIndexMaxElement(uint32_t len, int32_t* val);
};

#endif /* DEMO_CLASS_H_ */
