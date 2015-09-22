// WORKS - reads A/D values into buffer as fast as possible (about 2.7 usec/sample)
// Could probably be modified to use two ADCs for twice the rate
// based on various sources

#include <string.h>
#include "ADC.h" 

ADC *adc = new ADC(); // adc object

volatile int ibuf;
volatile int obuf;

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
#define BUF_SIZE 256
#define NO_BUFFERS 4
//DMAMEM static uint16_t adcbuffer[BUF_SIZE];
DMAMEM static volatile uint16_t __attribute__((aligned(BUF_SIZE+0))) adcbuffer[NO_BUFFERS][BUF_SIZE];

void loop() {

  unsigned cycles;
  
  // clear buffer
  for (int i = 0; i < NO_BUFFERS; ++i){
    for (int j = 0; j < BUF_SIZE; ++j){
      adcbuffer[i][j] = 50000;
    }
  }
 
  Serial.println("setup");
  ibuf = 0;
  obuf = 0;
  setup_dma(23);  // 38 is temp sensor
  setup_adc(23);

  for (int i = 0; i < BUF_SIZE; ++i){
    while(obuf==ibuf);
    //Serial.write(0x00000000);
    //Serial.write(0xFFFFFFFF);
    //Serial.write(0x00000000);
    Serial.write((uint8_t *)adcbuffer[obuf],512);
    //Serial.write(0x00000000);
    //Serial.write(0xFFFFFFFF);
    //Serial.print(0x00000000);
    obuf=(obuf+1)&3;
  }
  
  for (;;) {}

}  // loop()




// #include "pdb.h"
#include <DMAChannel.h>


DMAChannel* dma = new DMAChannel(false);

void setup_dma(int pin) {

  // Configure the ADC and run at least one software-triggered
  // conversion.  This completes the self calibration stuff and
  // leaves the ADC in a state that's mostly ready to use
//  analogReadRes(16);
//  analogReference(INTERNAL); // INTERNAL OR DEFAULT
//  analogReadAveraging(32);
//  analogRead(pin);
//  delay(1);

#if 0
  // set the programmable delay block to trigger DMA requests
  SIM_SCGC6 |= SIM_SCGC6_PDB; // enable PDB clock
  PDB0_IDLY = 0; // interrupt delay register
  PDB0_MOD = PDB_PERIOD; // modulus register, sets period
  PDB0_SC = PDB_CONFIG | PDB_SC_LDOK; // load registers from buffers
  PDB0_SC = PDB_CONFIG | PDB_SC_SWTRIG; // reset and restart
  PDB0_CH0C1 = 0x0101; // channel n control register?
#endif

  dma->begin(true);              // allocate the DMA channel first
  dma->TCD->SADDR = &ADC0_RA;    // where to read from
  dma->TCD->SOFF = 0;            // source increment each transfer
  dma->TCD->ATTR = DMA_TCD_ATTR_SSIZE(1);
  dma->TCD->NBYTES_MLNO = 2;     // bytes per transfer
  dma->TCD->SLAST = 0;

  dma->destinationBuffer(adcbuffer[0], 512);   // destinaton sizeof(adcbuffer[0])
  ibuf = 0;
  dma->triggerAtHardwareEvent(DMAMUX_SOURCE_ADC0);
  dma->disableOnCompletion();    // require restart in code
  dma->interruptAtCompletion();
  dma->attachInterrupt(call_dma_isr);
  
  dma->enable();

  

  // start first one

//  ADC0_SC2 |= ADC_SC2_DMAEN;  // using software trigger, ie writing to ADC0_SC1A
//  ADC0_SC3 |= ADC_SC3_ADCO;
//  ADC0_SC1A = get_pin(pin);   // set to hardware input channel
  
}  // setup_dma()

void setup_adc(int pin) {
  adc->setAveraging(32); // set number of averages
  adc->setResolution(16); // set bits of resolution
  adc->setReference(INTERNAL);
  adc->adc0->enableDMA(); //ADC0_SC2 |= ADC_SC2_DMAEN;  // using software trigger, ie writing to ADC0_SC1A
  adc->adc0->startContinuous(pin);//  ADC0_SC3 |= ADC_SC3_ADCO;  ADC0_SC1A = get_pin(pin);   // set to hardware input channel
  
} 


void call_dma_isr(void) {
    ibuf=(ibuf+1)&3;
    dma->destinationBuffer(adcbuffer[ibuf],512); //sizeof(adcbuffer[ibuf])
    dma->enable();
    dma->clearInterrupt();
    //Serial.println("call dma isr");
}

// convert pin name to hardware pin
// teensy 3.1 only

#if defined(__MK20DX256__)

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

}   // get_pin()

#endif
