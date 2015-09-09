/*
Author: Elias Vansteenkiste
*/


#undef HID_ENABLED
#define WINDOW_X512BYTES 1920

// Arduino Due ADC->DMA->USB 1MSPS
// Input: Analog in A0
// Output: Raw stream of uint16_t in range 0-4095 on Native USB Serial/ACM

// on linux, to stop the OS cooking your data: 
// stty -F /dev/ttyACM0 raw -iexten -echo -echoe -echok -echoctl -echoke -onlcr

volatile int bufn,obufn;
uint16_t buf[4][256];   // 4 buffers of 256 readings

void ADC_Handler(){     // move DMA pointers to next buffer
 int f=ADC->ADC_ISR;
 if (f&(1<<27)){
 //if (ADC->ADC_ISR & ADC_ISR_EOC7){
 //TODO probeer dit is, moet normaalgezien hetzelfde zijn, if (ADC->ADC_ISR & ADC_ISR_EOC7){    // ensure there was an End-of-Conversion and read the ISR reg
  bufn=(bufn+1)&3;
  ADC->ADC_RNPR=(uint32_t)buf[bufn]; // (Receive Next Pointer Register) - next DMA buffer 
  ADC->ADC_RNCR=256; // (Receive Next Counter Register) - set the counter to the size of the buffer
 } 
}

void setup(){
 pmc_enable_periph_clk(ID_ADC);// Is this necessary, normally used for dac? start clocking
 adc_init(ADC, SystemCoreClock, ADC_FREQ_MAX/32, ADC_STARTUP_FAST);
 ADC->ADC_MR |=0x80; // free running (Mode Register )
 //ADC->ADC_MR |= 0x2680; // these lines set free running mode on adc 7 (pin A0)  [PRESCAL at  50kHz] // TODO change PRESCAL on the adc init line

 ADC->ADC_CHER=0b11000000; // (Channel Enable Register) enable channel bit corresponding analog input port A0 A1

 NVIC_EnableIRQ(ADC_IRQn);// enable ADC interrupt vector
 ADC->ADC_IDR=~(1<<27); // (Interrupt Disable Register) -  disable interrupts
 ADC->ADC_IER=1<<27; // (Interrupt Enable Register) //enable ADC interrupt on ????
 // probeer dit eens uit ADC->ADC_IER = 0x80 ;         // enable AD7 End-Of-Conv interrupt (Arduino pin A0)
 // probeer dit eesn uit ADC->ADC_CGR = 0x15555555 ;   // All gains set to x1
 //ADC->ADC_CGR = 0xF000; //
 ADC->ADC_CGR = ADC_CGR_GAIN0(01) | ADC_CGR_GAIN1(11); // werkt nog niet
 ADC->ADC_COR = ADC_COR_OFF0 | ADC_COR_OFF1 ;
 
 ADC->ADC_RPR=(uint32_t)buf[0];   // Receive Pointer Register - DMA buffer
 ADC->ADC_RCR=256; // (Receive Counter Register) - set the counter to the size of the buffer
 ADC->ADC_RNPR=(uint32_t)buf[1]; // next DMA buffer (Receive Next Pointer Register)
 ADC->ADC_RNCR=256; // (Receive Next Counter Register) - set the counter to the size of the buffer
 bufn=obufn=1;
 ADC->ADC_PTCR=1; // (Transfer Control Register) //necessary?
 
 ADC->ADC_CR=2; // Starts ADC conversion. //necessary?
 // probeer dit eens   NVIC_SetPriority(ADC_IRQn,6); 

}

void loop(){
  SerialUSB.begin(115200); // baud rate ignored for usb virtual serial
  while(!SerialUSB);
  // data acquisition will start with a synchronisation step:
  // python should send a single byte of data, the arduino will send one back to sync timeouts
  int incoming = 0;
  while(SerialUSB.available() == 0) // polls whether anything is ready on the read buffer - nothing happens until there's something there
  incoming = SerialUSB.read();
  // after data received, send the same back
  SerialUSB.println(incoming);
  SerialUSB.println("Ready");
  //wait a little time for python to be ready to receive data - (not sure if this is really necessary)
  delay(50); // ms
  for(int i=0;i<WINDOW_X512BYTES;i++){
     while(obufn==bufn); // wait for buffer to be full
     SerialUSB.write((uint8_t *)buf[obufn],512); // send it - 512 bytes = 256 uint16_t
     obufn=(obufn+1)&3; //modulo 4 by doing a bitwise AND operation with 3 (=0011)  
  } 
  
}

