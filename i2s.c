#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

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

void cargar_Cancion(){
  printf("Inicio\n");
  i2s_Width_word_write(16);
  i2s_Divisor_BCK_write(35);
  i2s_Divisor_SCL_write(9);
  printf("Cargo datos\n");
  cargar_datos();
  printf("empieza a reproducir\n");
  i2s_Start_write(1);
}

int sen_1kHz_2c_16b[] = {16383, 17549, 18709, 19857, 20988, 22095, 23174, 24218, 25222, 26181,27091, 27946, 28743, 29477, 30145, 30742, 31267, 31717, 32088, 32380, 32591, 32720, 32765, 32728, 32608, 32405, 32121, 31757, 31316, 30798, 30208, 29547, 28819, 28029, 27179, 26275, 25320, 24320, 23280, 22205, 21100, 19971, 18824, 17665, 16499, 15333, 14172, 13022, 11889, 10799, 9698, 8650, 7642, 6678, 5763, 4902, 4099, 3358, 2684, 2079, 1547, 1090, 711, 411, 192, 55, 1, 30, 142, 336, 612, 968, 1402, 1912, 2496, 3149, 3870, 4655, 5499, 6398, 7348, 8344, 9380, 10451, 11554, 12680, 13825, 14984, 16149};
void cargar_datos(){
  int j=0;
	//printf("Dato de control %d\n", i2s_ctr_memoria_1_read());
	//printf("Dato de control %d\n", i2s_ctr_memoria_2_read());
  i2s_Start_save_write(1);
  while(j<44099){
      //printf("dato numero %d\n", j);
      //printf("%d\n", sen_1kHz_2c_16b[i%89]);
      i2s_to_memory_write(sen_1kHz_2c_16b[j%89]);
      i2s_r_en_write(1);
      j++;
  }
  printf("una memoria cargada\n");
  i2s_Start_save_write(0);
  //printf("Dato de control %d\n", i2s_ctr_memoria_read());

}
