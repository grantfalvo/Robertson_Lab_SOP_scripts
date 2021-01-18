const int x_dir_pin = 2;
const int x_step_pin = 3; 
const int x_limit_switch_pin = 4;
const int y1_dir_pin = 5;
const int y1_step_pin = 6; 
const int y_limit_switch_pin = 7;
const int y2_dir_pin = 8;
const int y2_step_pin = 9; 
const int z_dir_pin = 10;
const int z_step_pin = 11; 
const int z_limit_switch_pin = 12;

int stepsPerRevolution = 1600; // Pulses per Revolution
int motor_speed = 100; // delay between pulses (microseconds) 
float revolutions_per_cm = 2.54*(1.0/2.9); // measure this // note that the z axis is different. 
float z_revolutions_per_cm = 2.54*1.0; // measure this
int steps_per_cm = stepsPerRevolution*revolutions_per_cm;
int z_steps_per_cm = stepsPerRevolution*z_revolutions_per_cm;
float flush_lines_height = 2.0; // cm below limit switch
float sample_height = 3.0; // cm below limit switch
int x_limit_switch=HIGH;
int y_limit_switch=HIGH;
int z_limit_switch=digitalRead(z_limit_switch_pin);
float x_limit = 70; //cm from origin
float y_limit = 75; //cm from origin
float coordinates[3];

void setup() {
  pinMode(x_step_pin, OUTPUT);
  pinMode(x_dir_pin, OUTPUT);
  pinMode(x_limit_switch, INPUT);
  pinMode(y1_step_pin, OUTPUT);
  pinMode(y1_dir_pin, OUTPUT);
  pinMode(y_limit_switch, INPUT);
  pinMode(y2_step_pin, OUTPUT);
  pinMode(y2_dir_pin, OUTPUT);
  pinMode(z_step_pin, OUTPUT);
  pinMode(z_dir_pin, OUTPUT);
  pinMode(z_limit_switch, INPUT_PULLUP);
  float x_position=0;
  float y_position=0;
  float z_position=0;
  Serial.begin(9600);
  
}

void loop() {

  if (Serial.available() > 0) {
    String incoming_command = Serial.readStringUntil('\n');
    if (incoming_command == "Home"){
        Home();
      }
    if (incoming_command == "flush_lines"){
        flush_lines();
      }
    if (incoming_command == "sample"){
        sample();
      }
    if (incoming_command == "next_position"){ 
    Serial.println("next_position");
    delay(50);
    if (Serial.available() > 0) {
    // parse message for coordinates
    String incoming_message1 = Serial.readStringUntil('\n');
    char incoming_message[int(1+(incoming_message1).length())];
   incoming_message1.toCharArray(incoming_message, incoming_message1.length());
   const char s[] = ",";
   char* incoming_x_coordinate;
   char* incoming_y_coordinate;
   incoming_x_coordinate = strtok(incoming_message, s);
   incoming_y_coordinate = strtok(NULL, s); 
   next_position(incoming_x_coordinate,incoming_y_coordinate); 
  }
}
}
}

void Home(){

// home z motor
    int z_limit_switch=digitalRead(z_limit_switch_pin);
    digitalWrite(z_dir_pin, HIGH);    // High is  (up), LOW is  (down)
    while (z_limit_switch==HIGH) {   // HIGH is not pressed, LOW is pressed
    z_limit_switch=digitalRead(z_limit_switch_pin);  
    digitalWrite(z_step_pin, HIGH);
    delayMicroseconds(motor_speed*2);
    digitalWrite(z_step_pin, LOW);
    delayMicroseconds(motor_speed*2);
   }
    digitalWrite(z_dir_pin, LOW); 
    for (int i = 0; i < z_steps_per_cm; i++) {
    digitalWrite(z_step_pin, HIGH);
    delayMicroseconds(motor_speed*2);
    digitalWrite(z_step_pin, LOW);
    delayMicroseconds(motor_speed*2);
  }
    coordinates[2]=0+(z_steps_per_cm/z_steps_per_cm);

// home x motor
  x_limit_switch=digitalRead(x_limit_switch_pin); 
  digitalWrite(x_dir_pin, HIGH);    // High is negative (left), LOW is Positive (Right)
   while (x_limit_switch==HIGH) {   // HIGH is not pressed, LOW is pressed
    x_limit_switch=digitalRead(x_limit_switch_pin);  
    digitalWrite(x_step_pin, HIGH);
    delayMicroseconds(motor_speed*2);
    digitalWrite(x_step_pin, LOW);
    delayMicroseconds(motor_speed*2);
   }
    x_limit_switch=digitalRead(x_limit_switch_pin); 
    digitalWrite(x_dir_pin, LOW); 
    for (int i = 0; i < steps_per_cm; i++) {
    digitalWrite(x_step_pin, HIGH);
    delayMicroseconds(motor_speed*2);
    digitalWrite(x_step_pin, LOW);
    delayMicroseconds(motor_speed*2);
  }
    coordinates[0]=0+(steps_per_cm/steps_per_cm);

// home y motor
  y_limit_switch=digitalRead(y_limit_switch_pin); 
  digitalWrite(y1_dir_pin, HIGH);    // High is negative (down), LOW is Positive (up)
  digitalWrite(y2_dir_pin, HIGH);
   while (y_limit_switch==HIGH) {   // HIGH is not pressed, LOW is pressed
    y_limit_switch=digitalRead(y_limit_switch_pin);  
    digitalWrite(y1_step_pin, HIGH);
    digitalWrite(y2_step_pin, HIGH);
    delayMicroseconds(motor_speed*2);
    digitalWrite(y1_step_pin, LOW);
    digitalWrite(y2_step_pin, LOW);
    delayMicroseconds(motor_speed*2);
   }
    y_limit_switch=digitalRead(y_limit_switch_pin); 
    digitalWrite(y1_dir_pin, LOW); 
    digitalWrite(y2_dir_pin, LOW);
    for (int i = 0; i < steps_per_cm; i++) {
    digitalWrite(y1_step_pin, HIGH);
    digitalWrite(y2_step_pin, HIGH);
    delayMicroseconds(motor_speed*2);
    digitalWrite(y1_step_pin, LOW);
    digitalWrite(y2_step_pin, LOW);
    delayMicroseconds(motor_speed*2);
  }
    coordinates[1]=0+(steps_per_cm/steps_per_cm);

 // send back command and new coordinates
    //float coordinates[]={x_position,y_position,z_position}; 
    delayMicroseconds(50);
    Serial.println("Home");
    Serial.println(coordinates[0]);
    delayMicroseconds(50);
    Serial.println(coordinates[1]);
    delayMicroseconds(50);
    Serial.println(coordinates[2]);
    
  }

void flush_lines(){
  
      // calculate distance and set z_direction pin
    float z_travel_distance;
    z_travel_distance = flush_lines_height - coordinates[2]; 
    if (z_travel_distance < 0.0) {
    digitalWrite(z_dir_pin, HIGH); } 
    if (z_travel_distance > 0.0) {
    digitalWrite(z_dir_pin, LOW); }
    
    // move to new z position
    unsigned long z_travel_steps= roundf(z_steps_per_cm*abs(z_travel_distance));
    for (int i = 0; i < z_travel_steps; i++) {
    digitalWrite(z_step_pin, HIGH);
    delayMicroseconds(motor_speed);
    digitalWrite(z_step_pin, LOW);
    delayMicroseconds(motor_speed); 
   }
   coordinates[2]=flush_lines_height;

 // send back command and new coordinates
    //float coordinates[]={x_position,y_position,z_position}; 
    delayMicroseconds(10);
    Serial.println("flush_lines");
    Serial.println(coordinates[0]);
    delayMicroseconds(10);
    Serial.println(coordinates[1]);
    delayMicroseconds(10);
    Serial.println(coordinates[2]);
  
  }

void sample(){
  
      // calculate distance and set z_direction pin
    float z_travel_distance;
    z_travel_distance = sample_height - coordinates[2]; 
    if (z_travel_distance < 0.0) {
    digitalWrite(z_dir_pin, HIGH); } 
    if (z_travel_distance > 0.0) {
    digitalWrite(z_dir_pin, LOW); }
    
    // move to new z position
    unsigned long z_travel_steps= roundf(z_steps_per_cm*abs(z_travel_distance));
    for (int i = 0; i < z_travel_steps; i++) {
    digitalWrite(z_step_pin, HIGH);
    delayMicroseconds(motor_speed);
    digitalWrite(z_step_pin, LOW);
    delayMicroseconds(motor_speed); 
   }
   coordinates[2]=sample_height;

 // send back command and new coordinates
    //float coordinates[]={x_position,y_position,z_position}; 
    delayMicroseconds(10);
    Serial.println("sample");
    Serial.println(coordinates[0]);
    delayMicroseconds(10);
    Serial.println(coordinates[1]);
    delayMicroseconds(10);
    Serial.println(coordinates[2]);
  
  }

void next_position(char *incoming_x_coordinate,char *incoming_y_coordinate){
 
   if (coordinates[2] >= 1.00){  // if z probe is above floor then move
  
    // calculate distance and set x_direction pin
    float x_travel_distance;
    x_travel_distance = atof(incoming_x_coordinate) - coordinates[0]; 
    if (x_travel_distance < 0.0) {
    digitalWrite(x_dir_pin, HIGH); } 
    if (x_travel_distance > 0.0) {
    digitalWrite(x_dir_pin, LOW); }
    
    // move to new x position
    unsigned long x_travel_steps= roundf(steps_per_cm*abs(x_travel_distance));
    for (int i = 0; i < x_travel_steps; i++) {
    digitalWrite(x_step_pin, HIGH);
    delayMicroseconds(motor_speed);
    digitalWrite(x_step_pin, LOW);
    delayMicroseconds(motor_speed); 
   }
   coordinates[0]=atof(incoming_x_coordinate);

    // calculate distance and set y_direction pin
    float y_travel_distance;
    y_travel_distance = atof(incoming_y_coordinate) - coordinates[1];
    if (y_travel_distance < 0.0) {
    digitalWrite(y1_dir_pin, HIGH);  
    digitalWrite(y2_dir_pin, HIGH); } 
    if (y_travel_distance > 0.0) {
    digitalWrite(y1_dir_pin, LOW);
    digitalWrite(y2_dir_pin, LOW); }
    
    // move to new y position
    unsigned long y_travel_steps= roundf(steps_per_cm*abs(y_travel_distance));
    for (int i = 0; i < y_travel_steps; i++) {
    digitalWrite(y1_step_pin, HIGH);
    digitalWrite(y2_step_pin, HIGH);
    delayMicroseconds(motor_speed);
    digitalWrite(y1_step_pin, LOW);
    digitalWrite(y2_step_pin, LOW);
    delayMicroseconds(motor_speed); 
   }
   coordinates[1]=atof(incoming_y_coordinate); 
   delayMicroseconds(10);
   Serial.println("next_position");
   Serial.println(coordinates[0]);
   delayMicroseconds(10);
   //Serial.println(coordinates[1]);
   Serial.println(y_travel_steps);
   delayMicroseconds(10);
   Serial.println(coordinates[2]);
   }
  }
