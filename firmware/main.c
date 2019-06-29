#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include <irq.h>
#include <uart.h>
#include <console.h>
#include <generated/csr.h>

static void wait_ms(unsigned int ms)
{
	timer0_en_write(0);
	timer0_reload_write(0);
	timer0_load_write(SYSTEM_CLOCK_FREQUENCY/1000*ms);
	timer0_en_write(1);
	timer0_update_value_write(1);
	while(timer0_value_read()) timer0_update_value_write(1);
}



int main(void)
{
	irq_setmask(0);
	irq_setie(1);
	uart_init();

	puts("\nexample 04  lm32-CONFIG PWM_new timer and uart"__DATE__" "__TIME__"\n");

	int i=0;
	int j=0;

	if(i2s_En_left_read() == 1 ){
		t=(1.0/44100.0)*i;
		s=(short int)(sin(2.0*M_PI*400.0*t)*32767.0);
		i2s_data_left_write(&s);
		i++;
	}else if(i2s_En_right_read() == 1 ){
		t=(1.0/44100.0)*j;
		s=(short int)(sin(2.0*M_PI*400.0*t)*32767.0);
		i2s_data_left_write(&s);
		j++;
	}


    uint8_t i=0;
	while(1) {
	    wait_ms(10000);
		printf("prueba %d  \n", i++);
	}

	return 0;
}
