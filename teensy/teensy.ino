// WORKS - reads A/D values into buffer as fast as possible (about 2.7 usec/sample)
// Could probably be modified to use two ADCs for twice the rate
// based on various sources

#include <string.h>
#include "ADC.h" 

#define BUF_SIZE 4*256
//DMAMEM static uint16_t adcbuffer[BUF_SIZE];
DMAMEM static volatile uint16_t __attribute__((aligned(BUF_SIZE+0))) adcbuffer[BUF_SIZE];

//! Size of buffer
uint16_t b_size = BUF_SIZE;
//! write pointer: Read here
uint16_t b_write = 0;

unsigned long previousTime = 0;
unsigned long interval = 10000;

ADC *adc = new ADC(); // adc object

void setup() {
  char password[] = "start";
  uint8_t index = 0;
  char c = '0';
  
  Serial.begin(9600); // USB is always 12 Mbit/sec
  delay(100);
  // data acquisition will start with a synchronisation step:
  while(index!=5){
    while(Serial.available() == 0){
      delay(100);// polls whether anything is ready on the read buffer - nothing happens until there's something there
    }
    c = Serial.read();
    if(password[index]==c){
      index++;
    }else{
      index = 0;
    }
    delay(1);
  }
  delay(1000);
  Serial.println("Ready");
  

}

void loop() {

  int i,j;
  unsigned cycles;

   // set up cycle counter
  ARM_DEMCR |= ARM_DEMCR_TRCENA;
  ARM_DWT_CTRL |= ARM_DWT_CTRL_CYCCNTENA;
  
  // clear buffer
  for (i = 0; i < BUF_SIZE; ++i)
      adcbuffer[i] = 0;
      
  Serial.println(adcbuffer[0]);
  Serial.println(adcbuffer[1]);
 
  Serial.println("do dma");
  setup_dma(23);  // 38 is temp sensor

  while (adcbuffer[1] == 0) {};
  cycles = ARM_DWT_CYCCNT;
  while (adcbuffer[2] == 0) {};
  

  Serial.println(ARM_DWT_CYCCNT - cycles);

#if 0
  for(j=0;j<100;){
    unsigned long currentTime = micros();
    if(currentTime-previousTime>interval){
      j++;
      print_buffer();
    }
  }
#endif
 
  for (;;) {}

}  // loop()


void print_buffer(){
  uint16_t buffer[BUF_SIZE];
  uint8_t i;
  Serial.println("Start reading buffer:");
  
  // copy results
  memcpy((void *)buffer,(void *)adcbuffer,sizeof(adcbuffer));
  
  // display results - see how many samples we got
  for (i = 0; i < b_size; ++i)
      Serial.println(buffer[i]);
}

#include <DMAChannel.h>

DMAChannel dma(false);

void setup_dma(int pin) {

#if 0
  // set the programmable delay block to trigger DMA requests
  SIM_SCGC6 |= SIM_SCGC6_PDB; // enable PDB clock
  PDB0_IDLY = 0; // interrupt delay register
  PDB0_MOD = PDB_PERIOD; // modulus register, sets period
  PDB0_SC = PDB_CONFIG | PDB_SC_LDOK; // load registers from buffers
  PDB0_SC = PDB_CONFIG | PDB_SC_SWTRIG; // reset and restart
  PDB0_CH0C1 = 0x0101; // channel n control register?
#endif

  dma.begin(true);              // allocate the DMA channel first
  dma.TCD->SADDR = &ADC0_RA;    // where to read from
  dma.TCD->SOFF = 0;            // source increment each transfer
  dma.TCD->ATTR = DMA_TCD_ATTR_SSIZE(1);
  dma.TCD->SLAST = 0;
  
  dma.destinationCircular(adcbuffer, sizeof(adcbuffer));   // destinaton
  dma.transferSize(2);     // bytes per transfer == TCD->NBYTES
  dma.transferCount(1);
  dma.interruptAtCompletion();
  dma.triggerAtHardwareEvent(DMAMUX_SOURCE_ADC0);
  //dma.disableOnCompletion();    // require restart in code
  dma.enable();
  dma.attachInterrupt(call_dma_isr);

  
  adc->setAveraging(32); // set number of averages
  adc->setResolution(16); // set bits of resolution
  adc->setReference(INTERNAL);
  adc->adc0->enableDMA(); //ADC0_SC2 |= ADC_SC2_DMAEN;  // using software trigger, ie writing to ADC0_SC1A
  adc->adc0->startContinuous(pin);//  ADC0_SC3 |= ADC_SC3_ADCO;  ADC0_SC1A = get_pin(pin);   // set to hardware input channel
  
} 

void call_dma_isr(void) {
    //write
    Serial.println("write ptr value");
    Serial.println(b_write);
    print_buffer();

    b_write = increase(b_write);
    dma.clearInterrupt();
}

// increases the pointer modulo 2*size-1
uint16_t increase(uint16_t p) {
    return (p + 1)&(b_size-1);
}

//bool isFull() {
//    return (b_end == (b_start ^ b_size));
//}


// convert pin name to hardware pin
// teensy 3.1 only

int 
get_pin(int pin)
{
 
static const uint8_t channel2sc1a[] = {
  5, 14, 8, 9, 13, 12, 6, 7, 15, 4,
  0, 19, 3, 19+128, 26, 18+128, 23,
  5+192, 5+128, 4+128, 6+128, 7+128, 4+192
// A15  26   E1   ADC1_SE5a  5+64
// A16  27   C9   ADC1_SE5b  5
// A17  28   C8   ADC1_SE4b  4
// A18  29   C10  ADC1_SE6b  6
// A19  30   C11  ADC1_SE7b  7
// A20  31   E0   ADC1_SE4a  4+64
};

int index;

  if (pin <= 13) {
    index = pin;      // 0-13 refer to A0-A13
  } else if (pin <= 23) {
    index = pin - 14; // 14-23 are A0-A9
  } else if (pin >= 26 && pin <= 31) {
    index = pin - 9;  // 26-31 are A15-A20
  } else if (pin >= 34 && pin <= 40) {
    index = pin - 24; // 34-37 are A10-A13, 38 is temp sensor,
                // 39 is vref, 40 is A14
  } else {
    return 5;
  }

return channel2sc1a[index];

} 
