// WORKS - reads A/D values into buffer as fast as possible (about 2.7 usec/sample)
// Could probably be modified to use two ADCs for twice the rate
// based on various sources

#include <string.h>
#include "DMAChannel.h"
#include "ADC.h" 

#define BUF_SIZE 512
#define NO_BUFFERS 4

ADC *adc = new ADC(); // adc object

DMAChannel* dma0 = new DMAChannel(false);
DMAChannel* dma1 = new DMAChannel(false);

const uint16_t ChannelsCfg [] =  { 0x46, 0x47, 0x4F, 0x44 };
const int ledPin = 13;

//DMAMEM volatile uint16_t adcbuffer[NO_BUFFERS][BUF_SIZE];
DMAMEM static volatile uint16_t __attribute__((aligned(BUF_SIZE+0))) adcbuffer[NO_BUFFERS][BUF_SIZE];
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
  Serial.println("Ready");
  
  // initialize the digital pin as an output.
  pinMode(ledPin, OUTPUT);
  

}

void loop() {
  
  // clear buffer
  for (int i = 0; i < NO_BUFFERS; ++i){
    for (int j = 0; j < BUF_SIZE; ++j){
      adcbuffer[i][j] = 50000;
    }
  }

  digitalWrite(ledPin, HIGH);   // set the LED on
  delay(500);                  // wait for a second
  digitalWrite(ledPin, LOW);    // set the LED off
  delay(500); 
 
  Serial.println("setup");
  delay(500); 
  ibuf = 0;
  obuf = 0;

   
  setup_adc();
  setup_dma(); 
//  Serial.println("dma0 Channel");
//  print_config(dma0);
//  Serial.println("\ndma1 Channel");
//  print_config(dma1);


  for (int i = 0; i < 512; ++i){
    while(obuf==ibuf);
    //Serial.write(0x00000000);
    //Serial.write(0xFFFFFFFF);
    //Serial.write(0x00000000);
    //Serial.write((uint8_t *)adcbuffer[obuf],512); 
    Serial.println(adcbuffer[obuf][0]); 
    //Serial.println("read buffer and send data");
    //Serial.write(0x00000000);
    //Serial.write(0xFFFFFFFF);
    //Serial.print(0x00000000);
    obuf=(obuf+1)&3;
  }
  
  for (;;) {}

}

void setup_dma() {

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

  dma0->begin(true);              // allocate the DMA channel first
  dma0->TCD->SADDR = &ADC0_RA;    // where to read from
  dma0->TCD->SOFF = 0;            // source increment each transfer
  dma0->TCD->ATTR = 0x101;
  dma0->TCD->NBYTES = 2;     // bytes per transfer
  dma0->TCD->SLAST = 0;
  dma0->TCD->DADDR = &adcbuffer[0][0];// where to write to
  dma0->TCD->DOFF = 2; 
  dma0->TCD->DLASTSGA = -256;
  dma0->TCD->BITER = 128;
  dma0->TCD->CITER = 128;    
  dma0->triggerAtHardwareEvent(DMAMUX_SOURCE_ADC0);
  dma0->disableOnCompletion();    // require restart in code
  dma0->interruptAtCompletion();
  dma0->attachInterrupt(dma0_isr);
  
  dma1->begin(true);              // allocate the DMA channel first
  dma1->TCD->SADDR = &ChannelsCfg[0];
  dma1->TCD->SOFF = 2;            // source increment each transfer
  dma1->TCD->ATTR = 0x101;
  dma1->TCD->SLAST = -8;
  dma1->TCD->BITER = 4;
  dma1->TCD->CITER = 4;
  dma1->TCD->DADDR = &ADC0_SC1A;
  dma1->TCD->DLASTSGA = 0;
  dma1->TCD->NBYTES = 2;
  dma1->TCD->DOFF = 0;
  dma1->triggerAtTransfersOf(*dma0);
  dma1->triggerAtCompletionOf(*dma0);
//  dma1->interruptAtCompletion();
//  dma1->attachInterrupt(dma1_isr);

  dma0->enable();
  dma1->enable();
  
} 

void print_config(DMAChannel* dma) {
    Serial.print("channel\t");
    Serial.println(dma->channel);
    Serial.print("SADDR\t");
    Serial.println((uint32_t)dma->TCD->SADDR);
    Serial.print("SOFF\t");
    Serial.println((uint32_t)dma->TCD->SOFF);
    Serial.print("ATTR\t");
    Serial.println((uint32_t)dma->TCD->ATTR);
    Serial.print("NBYTES\t");
    Serial.println((uint32_t)dma->TCD->NBYTES);
    Serial.print("SLAST\t");
    Serial.println((uint32_t)dma->TCD->SLAST);
    Serial.print("DADDR\t");
    Serial.println((uint32_t)dma->TCD->DADDR);
    Serial.print("DOFF\t");
    Serial.println((uint32_t)dma->TCD->DOFF);
    Serial.print("CITER\t");
    Serial.println((uint32_t)dma->TCD->CITER);
    Serial.print("DLASTSGA\t");
    Serial.println((uint32_t)dma->TCD->DLASTSGA);
    Serial.print("CSR\t");
    Serial.println((uint32_t)dma->TCD->CSR);
    Serial.print("BITER\t");
    Serial.println((uint32_t)dma->TCD->BITER);
}

void setup_adc() {
  //adc->setAveraging(32); // set number of averages
  adc->setResolution(16); // set bits of resolution
  adc->setReference(INTERNAL);
  adc->adc0->enableDMA(); //ADC0_SC2 |= ADC_SC2_DMAEN;  // using software trigger, ie writing to ADC0_SC1A
  //adc->adc0->startContinuous(pin);//  ADC0_SC3 |= ADC_SC3_ADCO;  ADC0_SC1A = get_pin(pin);   // set to hardware input channel
  ADC0_SC1A = ChannelsCfg[3];
  
} 


void dma0_isr(void) {
    Serial.println("call dma0 isr");
    ibuf=(ibuf+1)&3;
    //dma0->destinationBuffer(adcbuffer[ibuf],512); //sizeof(adcbuffer[ibuf])
    dma0->TCD->DADDR = &adcbuffer[ibuf][0];
    dma0->clearInterrupt();
    dma0->enable();
}

//void dma1_isr(void) {
//    dma1->clearInterrupt();
//    Serial.println("call dma1 isr");
//    Serial.println(dma0->TCD->CITER);
//    Serial.println(dma1->TCD->CITER);
//    Serial.println((uint32_t)dma0->TCD->DADDR);  
//}


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

