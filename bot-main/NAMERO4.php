<?php
ob_start();
$token = "@s_P_p1"; # Token
$tokensan3 = "@NameroBots"; # Token
$admin = file_get_contents("admin.txt");
$sudo = array("$admin","5180881216");
$Df = $admin;
$infobot=explode("\n",file_get_contents("info.txt"));
$usernamebot=$infobot['1'];
$no3mak=$infobot['6'];
define('API_KEY',$token);
function bot($method,$datas=[]){
    $url = "https://api.telegram.org/bot".API_KEY."/".$method;
    $ch = curl_init();
    curl_setopt($ch,CURLOPT_URL,$url);
    curl_setopt($ch,CURLOPT_RETURNTRANSFER,true);
    curl_setopt($ch,CURLOPT_POSTFIELDS,$datas);
    $res = curl_exec($ch);
    if(curl_error($ch)){
        var_dump(curl_error($ch));
    }else{
        return json_decode($res);
    }
}

require ("../../bots/SALEH.php"); 
  
$update = json_decode(file_get_contents("php://input"));
$message = $update->message ?? null;
$callback = $update->callback_query ?? null;
if($message){
$chat_id = $message->chat->id;
$text = $message->text ?? "";
$from_id = $message->from->id; 
$name = $message->from->first_name;
}
if($callback){
$data = $callback->data;
$chat_id = $callback->message->chat->id; 
$message_id = $callback->message->message_id;
$from_id = $callback->from->id;
$name = $callback->from->first_name; 
}
$S_P_P1 = $data ?? $text; 
if(!empty($NaMerOset["wellcom"])){
$start = $NaMerOset["wellcom"];
} else {
$start = "
• اهلا بك ([$name](tg://user?id=$from_id)) في البوت الخاص بي ❤
- هذه هي الرسالة الافتراضية لانك لم تقم بإضافة رسالة ترحيب بعد.
";
}
function buildKeyboard($NaMerOset, $name){
$keyboard = ["inline_keyboard" => []];
$keyboard["inline_keyboard"][] = [
['text' => $name, 'callback_data' => 'jghhg']
];
if (!empty($NaMerOset["azrari"])) {
$row = [];
foreach ($NaMerOset["azrari"] as $i => $btn) {
$row[] = ['text' => $btn, 'callback_data' => $btn];
if (count($row) == 2) { 
$keyboard["inline_keyboard"][] = $row;
$row = [];
}
}
if (!empty($row)) {
$keyboard["inline_keyboard"][] = $row;
}
}
return json_encode($keyboard);
}

if($text == "/start"){
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>$start,
'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,
'reply_markup'=>buildKeyboard($NaMerOset, $name)
]);
}

if($data == "home"){
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>$start,
'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,
'reply_markup'=>buildKeyboard($NaMerOset, $name)
]);
}
function backKeyboard(){
return json_encode([
'inline_keyboard'=>[
[['text'=>'• رجوع •','callback_data'=>'home']]
]
]);
} 
if($S_P_P1 and isset($NaMerOset["azrar"][$S_P_P1]["text"])){
$army = $NaMerOset["azrar"][$S_P_P1]["text"];
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>$army,
'disable_web_page_preview'=>true,
'reply_markup'=>backKeyboard()
]);
} 


$update = json_decode(file_get_contents('php://input'));
$message = $update->message;
$chat_id = $message->chat->id;
$text = $message->text;
$message_id = $update->callback_query->message->message_id;
$data = $update->callback_query->data;
$name = $up->from->first_name;
$update = json_decode(file_get_contents("php://input"));
$message = $update->message;
$reply_id              = $message->reply_to_message->from->id;
$type = $message->chat->type;

$name = $message->from->first_name;
if(isset($update->callback_query)){

$up = $update->callback_query;
$chat_id = $up->message->chat->id;
$from_id = $up->from->id;
$user = $up->from->username;
$name = $up->from->first_name;
$message_id = $up->message->message_id;
$data = $up->data;
}

$setting = json_decode(file_get_contents("setting.json"),true);
if (!file_exists("setting.json")) {
#	$put = [];
$setting["twasl"]["type"]="✅";
$setting["twasl"]["replymod"]="✅";

$setting["twasl"]["modetext1"]="✅";
$setting["twasl"]["modetext2"]="✅";
$setting["twasl"]["modetext3"]="✅";
$setting["twasl"]["modetext4"]="✅";
$setting["twasl"]["modetext5"]="✅";
$setting["twasl"]["modetext6"]="✅";
$setting["twasl"]["modetext7"]="✅";
$setting["twasl"]["modetext8"]="✅";
$setting["twasl"]["modetext9"]="✅";
$setting["twasl"]["modetext10"]="✅";
file_put_contents("setting.json", json_encode($setting));
}
$replymod=$setting["twasl"]["replymod"];
$typeing=$setting["twasl"]["type"];


$modetext1 = $setting["twasl"]["modetext1"];
$modetext2= $setting["twasl"]["modetext2"];
$modetext3 = $setting["twasl"]["modetext3"];
$modetext4= $setting["twasl"]["modetext4"];
$modetext5= $setting["twasl"]["modetext5"];
$modetext6= $setting["twasl"]["modetext6"];
$modetext7= $setting["twasl"]["modetex7"];
$modetext8= $setting["twasl"]["modetext8"];
$modetext9= $setting["twasl"]["modetext9"];
$modetext10= $setting["twasl"]["modetext10"];

$photo=$message->photo;
$video=$message->video;
$document=$message->document;
$sticker=$message->sticker;
$voice=$message->voice;
$audio=$message->audio;


$modetext1 = $setting["twasl"]["modetext1"];
$modetext2= $setting["twasl"]["modetext2"];
$modetext3 = $setting["twasl"]["modetext3"];
$modetext4= $setting["twasl"]["modetext4"];
$modetext5= $setting["twasl"]["modetext5"];
$modetext6= $setting["twasl"]["modetext6"];
$modetext7= $setting["twasl"]["modetex7"];
$modetext8= $setting["twasl"]["modetext8"];
$modetext9= $setting["twasl"]["modetext9"];
$modetext10= $setting["twasl"]["modetext10"];


if($data == "bot9" or $data =="toch"){
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
◾️ إعدادات بوت التواصل ⚙️ .

▫️ ↴ يمكنك تغيير إعدادات البوت و تخصيص الإعدادات كم تريد .
",
'parse_mode'=>"MarkDown",
'reply_markup'=>json_encode([ 
'inline_keyboard'=>[
 [['text'=>"جاري الكتابه : $typeing",'callback_data'=>"onbott"],["text"=>" رد على الرسائل","callback_data"=>"estgbalon"]],
[['text'=>"تعين رساله الاستلام",'callback_data'=>"msrd"],['text'=>'تعين رساله الترحيب','callback_data'=>"setstart"]],
[['text'=>"قائمه الاومر",'callback_data'=>"hmaih"]],
[['text'=>"مكان الاستلام للرسائل  ",'callback_data'=>"bbuio"]],
[['text'=>"الوسائط الممنوعة",'callback_data'=>"man3er"]],
[['text'=>"رجوع",'callback_data'=>"back"]],
]])
]);
$setting["twasl"]["moder"]="s";
file_put_contents("setting.json", json_encode($setting));
}
if($data == "bromk"){
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
◾️ إعدادات بوت التواصل ⚙️ .

▫️ ↴ يمكنك تغيير إعدادات البوت و تخصيص الإعدادات كم تريد .
",
'reply_to_message_id'=>$message->message_id,
'parse_mode'=>"MarkDown",
'reply_markup'=>json_encode([ 
'inline_keyboard'=>[
[['text'=>"تفعيل التواصل ✅",'callback_data'=>"estgbalon"],['text'=>"تعطيل التواصل ❌ ",'callback_data'=>"estgbaloff"]],
]])
]);
$setting["twasl"]["moder"]="s";
file_put_contents("setting.json", json_encode($setting));
}

if($data == "bbuio"){
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
◾️ إعدادات مكان استلام الرسائل  .

▫️ ↴ اختر المكان الاتي تريد استقبال الرسائل فيها .
",
'parse_mode'=>"MarkDown",
'reply_markup'=>json_encode([ 
'inline_keyboard'=>[
 [['text'=>"في الخاص ",'callback_data'=>"typee"],["text"=>"في المجموعة  ","callback_data"=>"supergruope"]],
[['text'=>"رجوع",'callback_data'=>"back"]],
]])
]);
$setting["twasl"]["moder"]="s";
file_put_contents("setting.json", json_encode($setting));
}

if($data == "hmaih"){
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
↴قائمة اﻷوامر .
⚠️ جميع هذه الإوامر مع الرد على الرسالة .

▫️ارسل قفل او فتح الاومر التاليه :

🔸 الصور 
🔸 الملصقات
🔸 الفديو 
🔸 الملفات 
🔸 التوجيه 
🔸 الصوت 
🔸 الميوزك 
🔸 الروابط 
🔸 التوجيه 
🔸 قفل الكل : لقفل جميع الوسائط 
🔸 فتح الكل : لفتح جميع الوسائط 
▫️ حظر = لحظر شخص
▫️ الغاء حظر = لالغاء حظر عن شخص
▫️ معلومات = لعرض معلومات المستخدم

🛂 ملاحظه اذا اردت ارسال امر على سبيل المثال : قفل الصور او فتح الصور  ،
",
'parse_mode'=>"MarkDown",
'reply_markup'=>json_encode([ 
'inline_keyboard'=>[
[['text'=>" رجوع ",'callback_data'=>"bot9"]],
]
])
]);
}



if($data == "man3er" and $chat_id == $admin){
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
• الوسائط الممنوع إرسالها لك  🤖،

- ملاحظة🔭 :

✅  =  تعني - ممكن إرسالها لك،

❌  =  تعني - غير مسموح إرسالها لك،

",
'disable_web_page_preview'=>true,
"message_id"=>$message_id,
'reply_markup'=>json_encode(['inline_keyboard'=>[
[["text"=>"الصور ","callback_data"=>"#"],["text"=>"$modetext1","callback_data"=>"photo"]],
[["text"=>"الموسيقي ","callback_data"=>"#"],["text"=>"$modetext2","callback_data"=>"music"]],
[["text"=>"الملفات ","callback_data"=>"#"],["text"=>"$modetext3","callback_data"=>"file"]],
[["text"=>"الملصقات  ","callback_data"=>"#"],["text"=>"$modetext4","callback_data"=>"stick"]],
[["text"=>"االفيديو ","callback_data"=>"#"],["text"=>"$modetext5","callback_data"=>"video"]],
[["text"=>"الصوتيات ","callback_data"=>"#"],["text"=>"$modetext6","callback_data"=>"mov"]],
[["text"=>"جهه الاتصال ","callback_data"=>"#"],["text"=>"$modetext7","callback_data"=>"contact"]],
[["text"=>"اعاده توجيه ","callback_data"=>"#"],["text"=>"$modetext8","callback_data"=>"i3ad"]],
[["text"=>"جميع الروابط ","callback_data"=>"#"],["text"=>"$modetext9","callback_data"=>"alllink"]],
[["text"=>"روابط تيلجرام ","callback_data"=>"#"],["text"=>"$modetext10","callback_data"=>"linktele"]],
[['text'=>"رجوع",'callback_data'=>"back"]],
]])
  ]);
  $setting["twasl"]["moder"]="links";
file_put_contents("setting.json", json_encode($setting));
}


if($data== "photo"){
$setting = json_decode(file_get_contents("setting.json"),true);
$modetext2= $setting["twasl"]["modetext2"];
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
• الوسائط الممنوع إرسالها لك  🤖،

- ملاحظة🔭 :

✅  =  تعني - ممكن إرسالها لك،

❌  =  تعني - غير مسموح إرسالها لك،

",
'disable_web_page_preview'=>true,
"message_id"=>$message_id,
'reply_markup'=>json_encode(['inline_keyboard'=>[
[["text"=>"الصور ","callback_data"=>"#"],["text"=>"$modetext1","callback_data"=>"photo"]],
[["text"=>"الموسيقي ","callback_data"=>"#"],["text"=>"$modetext2","callback_data"=>"music"]],
[["text"=>"الملفات ","callback_data"=>"#"],["text"=>"$modetext3","callback_data"=>"file"]],
[["text"=>"الملصقات  ","callback_data"=>"#"],["text"=>"$modetext4","callback_data"=>"stick"]],
[["text"=>"االفيديو ","callback_data"=>"#"],["text"=>"$modetext5","callback_data"=>"video"]],
[["text"=>"الصوتيات ","callback_data"=>"#"],["text"=>"$modetext6","callback_data"=>"mov"]],
[["text"=>"جهه الاتصال ","callback_data"=>"#"],["text"=>"$modetext7","callback_data"=>"contact"]],
[["text"=>"اعاده توجيه ","callback_data"=>"#"],["text"=>"$modetext8","callback_data"=>"i3ad"]],
[["text"=>"جميع الروابط ","callback_data"=>"#"],["text"=>"$modetext9","callback_data"=>"alllink"]],
[["text"=>"روابط تيلجرام ","callback_data"=>"#"],["text"=>"$modetext10","callback_data"=>"linktele"]],
[['text'=>"رجوع",'callback_data'=>"back"]],
]])
]);
}
if($data == "photo" and $chat_id == $admin){
$setting = json_decode(file_get_contents("setting.json"),true);
$join=$setting["twasl"]["modetext1"];
if($join=="✅"){
$setting["twasl"]["modetext1"]="❌";
}
if($join=="❌"){
$setting["twasl"]["modetext1"]="✅";
}
file_put_contents("setting.json", json_encode($setting));
sendmessage($chat_id,$message_id);
}

#####99###

if($data== "music"){
$setting = json_decode(file_get_contents("setting.json"),true);
$modetext2= $setting["twasl"]["modetext2"];
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
• الوسائط الممنوع إرسالها لك  🤖،

- ملاحظة🔭 :

✅  =  تعني - ممكن إرسالها لك،

❌  =  تعني - غير مسموح إرسالها لك،

",
'disable_web_page_preview'=>true,
"message_id"=>$message_id,
'reply_markup'=>json_encode(['inline_keyboard'=>[
[["text"=>"الصور ","callback_data"=>"#"],["text"=>"$modetext1","callback_data"=>"photo"]],
[["text"=>"الموسيقي ","callback_data"=>"#"],["text"=>"$modetext2","callback_data"=>"music"]],
[["text"=>"الملفات ","callback_data"=>"#"],["text"=>"$modetext3","callback_data"=>"file"]],
[["text"=>"الملصقات  ","callback_data"=>"#"],["text"=>"$modetext4","callback_data"=>"stick"]],
[["text"=>"االفيديو ","callback_data"=>"#"],["text"=>"$modetext5","callback_data"=>"video"]],
[["text"=>"الصوتيات ","callback_data"=>"#"],["text"=>"$modetext6","callback_data"=>"mov"]],
[["text"=>"جهه الاتصال ","callback_data"=>"#"],["text"=>"$modetext7","callback_data"=>"contact"]],
[["text"=>"اعاده توجيه ","callback_data"=>"#"],["text"=>"$modetext8","callback_data"=>"i3ad"]],
[["text"=>"جميع الروابط ","callback_data"=>"#"],["text"=>"$modetext9","callback_data"=>"alllink"]],
[["text"=>"روابط تيلجرام ","callback_data"=>"#"],["text"=>"$modetext10","callback_data"=>"linktele"]],
[['text'=>"رجوع",'callback_data'=>"back"]],
]])
]);
}
if($data == "music" and $chat_id == $admin){
$setting = json_decode(file_get_contents("setting.json"),true);
$join=$setting["twasl"]["modetext2"];
if($join=="✅"){
$setting["twasl"]["modetext2"]="❌";
}
if($join=="❌"){
$setting["twasl"]["modetext2"]="✅";
}
file_put_contents("setting.json", json_encode($setting));
sendmessage($chat_id,$message_id);
}



#######444###


if($data== "file"){
$setting = json_decode(file_get_contents("setting.json"),true);
$modetext3 = $setting["twasl"]["modetext3"];
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
• الوسائط الممنوع إرسالها لك  🤖،

- ملاحظة🔭 :

✅  =  تعني - ممكن إرسالها لك،

❌  =  تعني - غير مسموح إرسالها لك،

",
'disable_web_page_preview'=>true,
"message_id"=>$message_id,
'reply_markup'=>json_encode(['inline_keyboard'=>[
[["text"=>"الصور ","callback_data"=>"#"],["text"=>"$modetext1","callback_data"=>"photo"]],
[["text"=>"الموسيقي ","callback_data"=>"#"],["text"=>"$modetext2","callback_data"=>"music"]],
[["text"=>"الملفات ","callback_data"=>"#"],["text"=>"$modetext3","callback_data"=>"file"]],
[["text"=>"الملصقات  ","callback_data"=>"#"],["text"=>"$modetext4","callback_data"=>"stick"]],
[["text"=>"االفيديو ","callback_data"=>"#"],["text"=>"$modetext5","callback_data"=>"video"]],
[["text"=>"الصوتيات ","callback_data"=>"#"],["text"=>"$modetext6","callback_data"=>"mov"]],
[["text"=>"جهه الاتصال ","callback_data"=>"#"],["text"=>"$modetext7","callback_data"=>"contact"]],
[["text"=>"اعاده توجيه ","callback_data"=>"#"],["text"=>"$modetext8","callback_data"=>"i3ad"]],
[["text"=>"جميع الروابط ","callback_data"=>"#"],["text"=>"$modetext9","callback_data"=>"alllink"]],
[["text"=>"روابط تيلجرام ","callback_data"=>"#"],["text"=>"$modetext10","callback_data"=>"linktele"]],
[['text'=>"رجوع",'callback_data'=>"back"]],
]])
]);
}
if($data == "file" and $chat_id == $admin){
$setting = json_decode(file_get_contents("setting.json"),true);
$join=$setting["twasl"]["modetext3"];
if($join=="✅"){
$setting["twasl"]["modetext3"]="❌";
}
if($join=="❌"){
$setting["twasl"]["modetext3"]="✅";
}
file_put_contents("setting.json", json_encode($setting));
sendmessage($chat_id,$message_id);
}



######8999###2

if($data== "stick"){
$setting = json_decode(file_get_contents("setting.json"),true);
$modetext4= $setting["twasl"]["modetext4"];
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
• الوسائط الممنوع إرسالها لك  🤖،

- ملاحظة🔭 :

✅  =  تعني - ممكن إرسالها لك،

❌  =  تعني - غير مسموح إرسالها لك،

",
'disable_web_page_preview'=>true,
"message_id"=>$message_id,
'reply_markup'=>json_encode(['inline_keyboard'=>[
[["text"=>"الصور ","callback_data"=>"#"],["text"=>"$modetext1","callback_data"=>"photo"]],
[["text"=>"الموسيقي ","callback_data"=>"#"],["text"=>"$modetext2","callback_data"=>"music"]],
[["text"=>"الملفات ","callback_data"=>"#"],["text"=>"$modetext3","callback_data"=>"file"]],
[["text"=>"الملصقات  ","callback_data"=>"#"],["text"=>"$modetext4","callback_data"=>"stick"]],
[["text"=>"االفيديو ","callback_data"=>"#"],["text"=>"$modetext5","callback_data"=>"video"]],
[["text"=>"الصوتيات ","callback_data"=>"#"],["text"=>"$modetext6","callback_data"=>"mov"]],
[["text"=>"جهه الاتصال ","callback_data"=>"#"],["text"=>"$modetext7","callback_data"=>"contact"]],
[["text"=>"اعاده توجيه ","callback_data"=>"#"],["text"=>"$modetext8","callback_data"=>"i3ad"]],
[["text"=>"جميع الروابط ","callback_data"=>"#"],["text"=>"$modetext9","callback_data"=>"alllink"]],
[["text"=>"روابط تيلجرام ","callback_data"=>"#"],["text"=>"$modetext10","callback_data"=>"linktele"]],
[['text'=>"رجوع",'callback_data'=>"back"]],
]])
]);
}
if($data == "stick" and $chat_id == $admin){
$setting = json_decode(file_get_contents("setting.json"),true);
$join=$setting["twasl"]["modetext4"];
if($join=="✅"){
$setting["twasl"]["modetext4"]="❌";
}
if($join=="❌"){
$setting["twasl"]["modetext4"]="✅";
}
file_put_contents("setting.json", json_encode($setting));
sendmessage($chat_id,$message_id);
}

#######8888##

if($data== "video"){
$setting = json_decode(file_get_contents("setting.json"),true);
$modetext5= $setting["twasl"]["modetext5"];
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
• الوسائط الممنوع إرسالها لك  🤖،

- ملاحظة🔭 :

✅  =  تعني - ممكن إرسالها لك،

❌  =  تعني - غير مسموح إرسالها لك،

",
'disable_web_page_preview'=>true,
"message_id"=>$message_id,
'reply_markup'=>json_encode(['inline_keyboard'=>[
[["text"=>"الصور ","callback_data"=>"#"],["text"=>"$modetext1","callback_data"=>"photo"]],
[["text"=>"الموسيقي ","callback_data"=>"#"],["text"=>"$modetext2","callback_data"=>"music"]],
[["text"=>"الملفات ","callback_data"=>"#"],["text"=>"$modetext3","callback_data"=>"file"]],
[["text"=>"الملصقات  ","callback_data"=>"#"],["text"=>"$modetext4","callback_data"=>"stick"]],
[["text"=>"االفيديو ","callback_data"=>"#"],["text"=>"$modetext5","callback_data"=>"video"]],
[["text"=>"الصوتيات ","callback_data"=>"#"],["text"=>"$modetext6","callback_data"=>"mov"]],
[["text"=>"جهه الاتصال ","callback_data"=>"#"],["text"=>"$modetext7","callback_data"=>"contact"]],
[["text"=>"اعاده توجيه ","callback_data"=>"#"],["text"=>"$modetext8","callback_data"=>"i3ad"]],
[["text"=>"جميع الروابط ","callback_data"=>"#"],["text"=>"$modetext9","callback_data"=>"alllink"]],
[["text"=>"روابط تيلجرام ","callback_data"=>"#"],["text"=>"$modetext10","callback_data"=>"linktele"]],
[['text'=>"رجوع",'callback_data'=>"back"]],
]])
]);
}
if($data == "video" and $chat_id == $admin){
$setting = json_decode(file_get_contents("setting.json"),true);
$join=$setting["twasl"]["modetext5"];
if($join=="✅"){
$setting["twasl"]["modetext5"]="❌";
}
if($join=="❌"){
$setting["twasl"]["modetext5"]="✅";
}
file_put_contents("setting.json", json_encode($setting));
sendmessage($chat_id,$message_id);
}


#########

if($data== "mov"){
$setting = json_decode(file_get_contents("setting.json"),true);
$modetext6= $setting["twasl"]["modetext6"];
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
• الوسائط الممنوع إرسالها لك  🤖،

- ملاحظة🔭 :

✅  =  تعني - ممكن إرسالها لك،

❌  =  تعني - غير مسموح إرسالها لك،

",
'disable_web_page_preview'=>true,
"message_id"=>$message_id,
'reply_markup'=>json_encode(['inline_keyboard'=>[
[["text"=>"الصور ","callback_data"=>"#"],["text"=>"$modetext1","callback_data"=>"photo"]],
[["text"=>"الموسيقي ","callback_data"=>"#"],["text"=>"$modetext2","callback_data"=>"music"]],
[["text"=>"الملفات ","callback_data"=>"#"],["text"=>"$modetext3","callback_data"=>"file"]],
[["text"=>"الملصقات  ","callback_data"=>"#"],["text"=>"$modetext4","callback_data"=>"stick"]],
[["text"=>"االفيديو ","callback_data"=>"#"],["text"=>"$modetext5","callback_data"=>"video"]],
[["text"=>"الصوتيات ","callback_data"=>"#"],["text"=>"$modetext6","callback_data"=>"mov"]],
[["text"=>"جهه الاتصال ","callback_data"=>"#"],["text"=>"$modetext7","callback_data"=>"contact"]],
[["text"=>"اعاده توجيه ","callback_data"=>"#"],["text"=>"$modetext8","callback_data"=>"i3ad"]],
[["text"=>"جميع الروابط ","callback_data"=>"#"],["text"=>"$modetext9","callback_data"=>"alllink"]],
[["text"=>"روابط تيلجرام ","callback_data"=>"#"],["text"=>"$modetext10","callback_data"=>"linktele"]],
[['text'=>"رجوع",'callback_data'=>"back"]],
]])
]);
}
if($data == "mov" and $chat_id == $admin){
$setting = json_decode(file_get_contents("setting.json"),true);
$join=$setting["twasl"]["modetext6"];
if($join=="✅"){
$setting["twasl"]["modetext6"]="❌";
}
if($join=="❌"){
$setting["twasl"]["modetext6"]="✅";
}
file_put_contents("setting.json", json_encode($setting));
sendmessage($chat_id,$message_id);
}


#########

if($data== "contact"){
$setting = json_decode(file_get_contents("setting.json"),true);
$modetext7= $setting["twasl"]["modetex7"];
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
• الوسائط الممنوع إرسالها لك  🤖،

- ملاحظة🔭 :

✅  =  تعني - ممكن إرسالها لك،

❌  =  تعني - غير مسموح إرسالها لك،

",
'disable_web_page_preview'=>true,
"message_id"=>$message_id,
'reply_markup'=>json_encode(['inline_keyboard'=>[
[["text"=>"الصور ","callback_data"=>"#"],["text"=>"$modetext1","callback_data"=>"photo"]],
[["text"=>"الموسيقي ","callback_data"=>"#"],["text"=>"$modetext2","callback_data"=>"music"]],
[["text"=>"الملفات ","callback_data"=>"#"],["text"=>"$modetext3","callback_data"=>"file"]],
[["text"=>"الملصقات  ","callback_data"=>"#"],["text"=>"$modetext4","callback_data"=>"stick"]],
[["text"=>"االفيديو ","callback_data"=>"#"],["text"=>"$modetext5","callback_data"=>"video"]],
[["text"=>"الصوتيات ","callback_data"=>"#"],["text"=>"$modetext6","callback_data"=>"mov"]],
[["text"=>"جهه الاتصال ","callback_data"=>"#"],["text"=>"$modetext7","callback_data"=>"contact"]],
[["text"=>"اعاده توجيه ","callback_data"=>"#"],["text"=>"$modetext8","callback_data"=>"i3ad"]],
[["text"=>"جميع الروابط ","callback_data"=>"#"],["text"=>"$modetext9","callback_data"=>"alllink"]],
[["text"=>"روابط تيلجرام ","callback_data"=>"#"],["text"=>"$modetext10","callback_data"=>"linktele"]],
[['text'=>"رجوع",'callback_data'=>"back"]],
]])
]);
}
if($data == "contact" and $chat_id == $admin){
$setting = json_decode(file_get_contents("setting.json"),true);
$join=$setting["twasl"]["modetex7"];
if($join=="✅"){
$setting["twasl"]["modetex7"]="❌";
}
if($join=="❌"){
$setting["twasl"]["modetex7"]="✅";
}
file_put_contents("setting.json", json_encode($setting));
sendmessage($chat_id,$message_id);
}

if($data== "i3ad"){
$setting = json_decode(file_get_contents("setting.json"),true);
$modetext8= $setting["twasl"]["modetext8"];
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
• الوسائط الممنوع إرسالها لك  🤖،

- ملاحظة🔭 :

✅  =  تعني - ممكن إرسالها لك،

❌  =  تعني - غير مسموح إرسالها لك،

",
'disable_web_page_preview'=>true,
"message_id"=>$message_id,
'reply_markup'=>json_encode(['inline_keyboard'=>[
[["text"=>"الصور ","callback_data"=>"#"],["text"=>"$modetext1","callback_data"=>"photo"]],
[["text"=>"الموسيقي ","callback_data"=>"#"],["text"=>"$modetext2","callback_data"=>"music"]],
[["text"=>"الملفات ","callback_data"=>"#"],["text"=>"$modetext3","callback_data"=>"file"]],
[["text"=>"الملصقات  ","callback_data"=>"#"],["text"=>"$modetext4","callback_data"=>"stick"]],
[["text"=>"االفيديو ","callback_data"=>"#"],["text"=>"$modetext5","callback_data"=>"video"]],
[["text"=>"الصوتيات ","callback_data"=>"#"],["text"=>"$modetext6","callback_data"=>"mov"]],
[["text"=>"جهه الاتصال ","callback_data"=>"#"],["text"=>"$modetext7","callback_data"=>"contact"]],
[["text"=>"اعاده توجيه ","callback_data"=>"#"],["text"=>"$modetext8","callback_data"=>"i3ad"]],
[["text"=>"جميع الروابط ","callback_data"=>"#"],["text"=>"$modetext9","callback_data"=>"alllink"]],
[["text"=>"روابط تيلجرام ","callback_data"=>"#"],["text"=>"$modetext10","callback_data"=>"linktele"]],
[['text'=>"رجوع",'callback_data'=>"back"]],
]])
]);
}
if($data == "i3ad" and $chat_id == $admin){
$setting = json_decode(file_get_contents("setting.json"),true);
$join=$setting["twasl"]["modetext8"];
if($join=="✅"){
$setting["twasl"]["modetext8"]="❌";
}
if($join=="❌"){
$setting["twasl"]["modetext8"]="✅";
}
file_put_contents("setting.json", json_encode($setting));
sendmessage($chat_id,$message_id);
}


#######

if($data== "alllink"){
$setting = json_decode(file_get_contents("setting.json"),true);
$modetext9= $setting["twasl"]["modetext9"];
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
• الوسائط الممنوع إرسالها لك  🤖،

- ملاحظة🔭 :

✅  =  تعني - ممكن إرسالها لك،

❌  =  تعني - غير مسموح إرسالها لك،

",
'disable_web_page_preview'=>true,
"message_id"=>$message_id,
'reply_markup'=>json_encode(['inline_keyboard'=>[
[["text"=>"الصور ","callback_data"=>"#"],["text"=>"$modetext1","callback_data"=>"photo"]],
[["text"=>"الموسيقي ","callback_data"=>"#"],["text"=>"$modetext2","callback_data"=>"music"]],
[["text"=>"الملفات ","callback_data"=>"#"],["text"=>"$modetext3","callback_data"=>"file"]],
[["text"=>"الملصقات  ","callback_data"=>"#"],["text"=>"$modetext4","callback_data"=>"stick"]],
[["text"=>"االفيديو ","callback_data"=>"#"],["text"=>"$modetext5","callback_data"=>"video"]],
[["text"=>"الصوتيات ","callback_data"=>"#"],["text"=>"$modetext6","callback_data"=>"mov"]],
[["text"=>"جهه الاتصال ","callback_data"=>"#"],["text"=>"$modetext7","callback_data"=>"contact"]],
[["text"=>"اعاده توجيه ","callback_data"=>"#"],["text"=>"$modetext8","callback_data"=>"i3ad"]],
[["text"=>"جميع الروابط ","callback_data"=>"#"],["text"=>"$modetext9","callback_data"=>"alllink"]],
[["text"=>"روابط تيلجرام ","callback_data"=>"#"],["text"=>"$modetext10","callback_data"=>"linktele"]],
[['text'=>"رجوع",'callback_data'=>"back"]],
]])
]);
}
if($data == "alllink" and $chat_id == $admin){
$setting = json_decode(file_get_contents("setting.json"),true);
$join=$setting["twasl"]["modetext9"];
if($join=="✅"){
$setting["twasl"]["modetext9"]="❌";
}
if($join=="❌"){
$setting["twasl"]["modetext9"]="✅";
}
file_put_contents("setting.json", json_encode($setting));
sendmessage($chat_id,$message_id);
}


############

if($data== "linktele"){
$setting = json_decode(file_get_contents("setting.json"),true);
$modetext10= $setting["twasl"]["modetext10"];
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
• الوسائط الممنوع إرسالها لك  🤖،

- ملاحظة🔭 :

✅  =  تعني - ممكن إرسالها لك،

❌  =  تعني - غير مسموح إرسالها لك،

",
'disable_web_page_preview'=>true,
"message_id"=>$message_id,
'reply_markup'=>json_encode(['inline_keyboard'=>[
[["text"=>"الصور ","callback_data"=>"#"],["text"=>"$modetext1","callback_data"=>"photo"]],
[["text"=>"الموسيقي ","callback_data"=>"#"],["text"=>"$modetext2","callback_data"=>"music"]],
[["text"=>"الملفات ","callback_data"=>"#"],["text"=>"$modetext3","callback_data"=>"file"]],
[["text"=>"الملصقات  ","callback_data"=>"#"],["text"=>"$modetext4","callback_data"=>"stick"]],
[["text"=>"االفيديو ","callback_data"=>"#"],["text"=>"$modetext5","callback_data"=>"video"]],
[["text"=>"الصوتيات ","callback_data"=>"#"],["text"=>"$modetext6","callback_data"=>"mov"]],
[["text"=>"جهه الاتصال ","callback_data"=>"#"],["text"=>"$modetext7","callback_data"=>"contact"]],
[["text"=>"اعاده توجيه ","callback_data"=>"#"],["text"=>"$modetext8","callback_data"=>"i3ad"]],
[["text"=>"جميع الروابط ","callback_data"=>"#"],["text"=>"$modetext9","callback_data"=>"alllink"]],
[["text"=>"روابط تيلجرام ","callback_data"=>"#"],["text"=>"$modetext10","callback_data"=>"linktele"]],
[['text'=>"رجوع",'callback_data'=>"back"]],
]])
]);
}
#########
if($data == "linktele" and $chat_id == $admin){
$setting = json_decode(file_get_contents("setting.json"),true);
$join=$setting["twasl"]["modetext10"];
if($join=="✅"){
$setting["twasl"]["modetext10"]="❌";
}
if($join=="❌"){
$setting["twasl"]["modetext10"]="✅";
}
file_put_contents("setting.json", json_encode($setting));
sendmessage($chat_id,$message_id);
}





if($data == "setsta" and $chat_id == $admin){
bot('EditMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
▫️ إرسل رسالة الترحيب التي تريد:
▪️ يمكنك إستخدام الـMarkdown .
-
-
",
'reply_markup'=>json_encode(['inline_keyboard'=>[
[["text"=>"• رجوع •","callback_data"=>"bot9"]],
]])
  ]);
$setting["twasl"]["mode"]="set2";
file_put_contents("setting.json", json_encode($setting));
}


if($text and $setting["twasl"]["mode"]=="set2" and $chat_id == $admin){
	bot('sendmessage',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
"text"=>"
$text
",
'disable_web_page_preview'=>true,
'parse_mode'=>"markdown",
]);
bot('sendmessage',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
"text"=>"

",
'disable_web_page_preview'=>true,
'parse_mode'=>"markdown",
'reply_markup'=>json_encode(['inline_keyboard'=>[
[["text"=>"• رجوع •","callback_data"=>"bot9"]],
]])
]);
$setting["twasl"]["start"]= $text;
$setting["twasl"]["mode"]=null;
file_put_contents("setting.json", json_encode($setting));
}

$he = $setting["twasl"]["moder"];
if($he== "s"){
function sendmessage($chat_id,$message_id){
$setting = json_decode(file_get_contents("setting.json"),true);
$typeing=$setting["twasl"]["type"];
$replymod=$setting["twasl"]["replymod"];
bot('EditMessageText',[
'chat_id'=>$chat_id, 
'text'=>"
◾️ إعدادات بوت التواصل ⚙️ .

▫️ ↴ يمكنك تغيير إعدادات البوت و تخصيص الإعدادات كم تريد .
",
'disable_web_page_preview'=>true,
"message_id"=>$message_id,
'reply_markup'=>json_encode(['inline_keyboard'=>[
 [['text'=>"جاري الكتابه : $typeing",'callback_data'=>"onbott"],["text"=>" رد على الرسائل","callback_data"=>"estgbalon"]],
[['text'=>"تعين رساله الاستلام",'callback_data'=>"msrd"],['text'=>'تعين رساله الترحيب','callback_data'=>"setstart"]],
[['text'=>"قائمه الاومر",'callback_data'=>"hmaih"]],
[['text'=>"مكان الاستلام للرسائل  ",'callback_data'=>"bbuio"]],
[['text'=>"الوسائط الممنوعة",'callback_data'=>"man3er"]],
[['text'=>"رجوع",'callback_data'=>"back"]],
]])
]);
} 
}

if($data == "onbott" and $chat_id == $admin){
$setting = json_decode(file_get_contents("setting.json"),true);
$join=$setting["twasl"]["type"];
if($join=="✅"){
$setting["twasl"]["type"]="❌";
}
if($join=="❌"){
$setting["twasl"]["type"]="✅";
}
file_put_contents("setting.json", json_encode($setting));
sendmessage($chat_id,$message_id);
}

if($data == "replymod" and $chat_id == $admin){
$setting = json_decode(file_get_contents("setting.json"),true);
$join=$setting["twasl"]["replymod"];
if($join=="✅"){
$setting["twasl"]["replymod"]="❌";
}
if($join=="❌"){
$setting["twasl"]["replymod"]="✅";
}
file_put_contents("setting.json", json_encode($setting));
sendmessage($chat_id,$message_id);
}



$update = json_decode(file_get_contents("php://input"));
file_put_contents("update.txt",json_encode($update));
$message = $update->message;
$text = $message->text;
$chat_id = $message->chat->id;
$from_id = $message->from->id;$type = $message->chat->type;
$message_id = $message->message_id;
$name = $message->from->first_name.' '.$message->from->last_name;
$user = strtolower($message->from->username);

$t =$message->chat->title; 

if(isset($update->callback_query)){
$up = $update->callback_query;
$chat_id = $up->message->chat->id;
$from_id = $up->from->id;
$user = strtolower($up->from->username); 
$name = $up->from->first_name.' '.$up->from->last_name;
$message_id = $up->message->message_id;
$mes_id = $update->callback_query->inline_message_id; 

$data = $up->data;
}

if(isset($update->inline_query)){
$chat_id = $update->inline_query->chat->id;
$from_id = $update->inline_query->from->id;
$name = $update->inline_query->from->first_name.' '.$update->inline_query->from->last_name;
$text_inline = $update->inline_query->query;
$mes_id = $update->inline_query->inline_message_id; 

$user = strtolower($update->inline_query->from->username); 
}
$caption = $update->message->caption;
function getChatstats1($chat_id,$token) {
  $url = 'https://api.telegram.org/bot'.$token.'/getChatAdministrators?chat_id='.$chat_id;
  $result = file_get_contents($url);
  $result = json_decode ($result);
  $result = $result->ok;
  return $result;
}
 function getmember($token,$idchannel,$from_id) {
  $join = file_get_contents("https://api.telegram.org/bot".$token."/getChatMember?chat_id=$idchannel&user_id=".$from_id);
if((strpos($join,'"status":"left"') or strpos($join,'"Bad Request: USER_ID_INVALID"') or strpos($join,'"Bad Request: user not found"') or strpos($join,'"ok": false') or strpos($join,'"status":"kicked"')) !== false){
$KhAlEdJ="no";}else{$KhAlEdJ="yes";}
return $KhAlEdJ;


}
@mkdir("sudo");
@mkdir("data");
$member = explode("\n",file_get_contents("sudo/member.txt"));
$cunte = count($member)-1;
$ban = explode("\n",file_get_contents("sudo/ban.txt"));
$countban = count($ban)-1;
$admin=file_get_contents("admin.txt");

@$KhAlEdJjson = json_decode(file_get_contents("../KhAlEdJ.json"),true);
$st_ch_bots=$KhAlEdJjson["info"]["st_ch_bots"];
$id_ch_sudo1=$KhAlEdJjson["info"]["id_channel"];
$link_ch_sudo1=$KhAlEdJjson["info"]["link_channel"];
$id_ch_sudo2=$KhAlEdJjson["info"]["id_channel2"];
$link_ch_sudo2=$KhAlEdJjson["info"]["link_channel2"];
$user_bot_sudo=$KhAlEdJjson["info"]["user_bot"];


@$projson = json_decode(file_get_contents("pro.json"),true);
$pro=$projson["info"]["pro"];

$dateon=$projson["info"]["dateon"];

$dateoff=$projson["info"]["dateoff"];


$time=time()+(3600 * 1);

if($pro!="yes" or $pro==null){
#if($time < $dateoff){
$txtfree='<a href="https://t.me/'.$user_bot_sudo.'">• اضغط هنا لنصع '.$no3mak.' خاص بك </a>';
#}
}



$update = json_decode(file_get_contents("php://input"));
$message = $update->message;
$txt = $message->caption;
$text = $message->text;
$chat_id = $message->chat->id;
$from_id = $message->from->id;
$new = $message->new_chat_members;
$message_id = $message->message_id;
$type = $message->chat->type;
$name = $message->from->first_name;
if(isset($update->callback_query)){
$callbackMessage = '';
var_dump(bot('answerCallbackQuery',[
'callback_query_id'=>$update->callback_query->id,
'text'=>$callbackMessage]));
$up = $update->callback_query;
$chat_id = $up->message->chat->id;
$from_id = $up->from->id;
$user = $up->from->username;
$name = $up->from->first_name;
$message_id = $up->message->message_id;
$data = $up->data;
}
$id = $update->inline_query->from->id; 
//$admin = $admin; 
mkdir("sudo");
mkdir("message");
mkdir("data");
mkdir("ms");
mkdir("count");
mkdir("count/user");
mkdir("count/admin");
$START= file_get_contents("data/start.txt");
$getmes_id = explode("\n", file_get_contents("ms/$message_id.txt"));
$get_ban=file_get_contents('data/ban.txt');
$ban =explode("\n",$get_ban);
/////////////////////

$member = explode("\n",file_get_contents("sudo/member.txt"));
$cunte = count($member)-1;
//////////

$amr = file_get_contents("sudo/amr.txt");
$ch1 = file_get_contents("sudo/ch1.txt");
$ch2= file_get_contents("sudo/ch2.txt");
$taf3il = file_get_contents("sudo/tanbih.txt");
$estgbal = file_get_contents("sudo/estgbal.txt");

 //ايديك
$reply = $message->reply_to_message->message_id;
$rep = $message->reply_to_message->forward_from; 

////======================\\\\

if($message){
$join = file_get_contents("https://api.telegram.org/bot$token/getChatMember?chat_id=$ch1&user_id=$from_id");
$join2 = file_get_contents("https://api.telegram.org/bot$token/getChatMember?chat_id=$ch2&user_id=$from_id");

if($message && (
strpos($join,'"status":"left"') 
or
strpos($join,'"Bad Request: USER_ID_INVALID"')
or
strpos($join,'"Bad Request: user not found"')
or
strpos($join,'"ok": false')
or strpos($join,'"status":"kicked"') or 
strpos($join2,'"status":"left"') 
or 
strpos($join2,'"Bad Request: USER_ID_INVALID"') 
or 
strpos($join2,'"Bad Request: user not found"') 
or
strpos($join2,'"ok": false') 
or strpos($join2,'"status":"kicked"'))!== false){
$ch1=str_replace("@","",$ch1);
$ch2=str_replace("@","",$ch2);
bot('sendMessage',[
'chat_id'=>$chat_id,
'reply_to_message_id'=>$message_id,
'text'=>"

",
'disable_web_page_preview'=>true,
'parse_mode'=>"markdown",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
]
])
]);
return false;}}




#####
if($data == "typee"){
bot('EditMessageText',[
    'chat_id'=>$chat_id,
    'message_id'=>$message_id,
'text'=>'• تم التفعيل مسبقا !',
 'reply_markup'=>json_encode([ 
      'inline_keyboard'=>[
[['text'=>'رجوع ' ,'callback_data'=>"bot9"]],
]])
]);
file_put_contents("sudo/typee.txt","$from_id");
}


if($data == "supergruope"){
bot('EditMessageText',[
    'chat_id'=>$chat_id,
    'message_id'=>$message_id,
'text'=>'
◾️ يمكنك استقبال الرسائل في مجموعتك انت وفريقك او اصدقائك  .

▫️ ↴ اضغط على الزر من ثم قم بختيار المجموعة الاتي تريد استقبال الرسائل فيها ثم أرسل تفعيل،
-
',
 'reply_markup'=>json_encode([ 
      'inline_keyboard'=>[
[['text'=>"• اضفني الى مجموعتك • ",'switch_inline_query'=>""]],
[['text'=>'رجوع ' ,'callback_data'=>"bot9"]],
]])
]);
file_put_contents("sudo/amr.txt","set");
}
if($text=="تفعيل" and $amr == "set" and in_array($from_id, $sudo)){
file_put_contents("sudo/amr.txt","");
bot('sendmessage',[
    'chat_id'=>$chat_id,
    'message_id'=>$message_id,
'text'=>'- حسناا عزيزي تم تحديد الكروب بنجاح سيتم نشر الرسائل في الكروب✅ ".',
]);
file_put_contents("sudo/typee.txt","$chat_id");
}
if($data == "estgbalon"){
bot('EditMessageText',[
    'chat_id'=>$chat_id,
    'message_id'=>$message_id,
'text'=>' - تم تفعيل الرد بنجاح ✅،',
 'reply_markup'=>json_encode([ 
      'inline_keyboard'=>[
[['text'=>'رجوع ' ,'callback_data'=>"bot9"]],
]])
]);
file_put_contents("sudo/estgbal.txt","on");
}

if($data == "estgbaloff"){
bot('EditMessageText',[
    'chat_id'=>$chat_id,
    'message_id'=>$message_id,
'text'=>' تم تعطيل توجيه الرسائل ✅".',
 'reply_markup'=>json_encode([ 
      'inline_keyboard'=>[
[['text'=>'رجوع ".' ,'callback_data'=>"bot9"]],
]])
]);
unlink("sudo/amr.txt");
unlink("sudo/estgbal.txt");
}


if($data == 'msrd'){
bot('editMessageText',[
'chat_id'=>$chat_id,
'message_id'=>$message_id,
'text'=>"
▫️ إرسل رسالة التسليم التي تريد:
▪️ يمكنك إستخدام الـMarkdown .
-
",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>'رجوع','callback_data'=>'bot9']]    
]    
])
]);
file_put_contents("sudo/amr.txt","msrd");
}

if($text and $amr == "msrd" and in_array($from_id, $sudo)){
unlink("sudo/amr.txt");
bot('sendmessage',[
	'chat_id'=>$chat_id,
'text'=>"
-  تم إضافة ( رسالة تسليم ) إلى بوت التواصل الخاص بك .
▫️ مثل على رسالة التسليم ( $text ) 🥏
",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>'رجوع','callback_data'=>'bot9']]    
]    
])
]);
file_put_contents("data/msrd.txt","$text");
}




$yppee=file_get_contents("sudo/typee.txt");
if($yppee==null or $yppee==""){
$yppee=$admin;

}
$get_ban=file_get_contents('data/ban.txt');
$ban =explode("\n",$get_ban);



///====  الاعضاء  ====\\\\
$start= file_get_contents("data/start.txt");
$ainfo= file_get_contents("data/ainfo.txt");
$chan= file_get_contents("data/chan.txt");
$law= file_get_contents("data/law.txt");
$infobot= file_get_contents("data/infobot.txt");
$msrd= file_get_contents("data/msrd.txt");




$yppee=file_get_contents("sudo/typee.txt");
if($yppee==null or $yppee==""){
$yppee=$admin;

}

$co_m_all=file_get_contents("count/user/all.txt");
$co1=$co_m_all+1;



$repp=$message->reply_to_message->message_id-1;
$msg=explode("=",file_get_contents("message/$repp.txt"));

$get_ban=file_get_contents('data/ban.txt');
$get_ban=file_get_contents('data/ban.txt');
$ban =explode("\n",$get_ban);
if($text){

if($text != '/start' and $text != 'جهة اتصال المدير☎️' and $text != '⚜️〽️┇قناه البوت' and $text != 'ارفعني' and $text != 'القوانين ⚠️' and $text != 'معلومات المدير 📋' and   $text !='المساعده 💡' and $text !='اطلب بوتك من المطور' and $message->chat->type == 'private' and $from_id != $admin ){
if(!in_array($from_id, $ban)){
if($estgbal=="on" or $estgbal==null){
bot('sendMessage',[
'chat_id'=>$yppee,
'text'=>"
",
'reply_to_message_id'=>$message->reply_to_message->message_id-1,
'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,

]);

$get= bot('forwardMessage',[
'chat_id'=>$yppee,
'from_chat_id'=>$chat_id,
'message_id'=>$message_id,

]);
$msg_id = $get->result->message_id-1;

$from_id_name="$chat_id=$name=$message_id";
file_put_contents("message/$msg_id.txt","$from_id_name");

$co_m_us=file_get_contents("count/user/$from_id.txt");
$co=$co_m_us+1;
file_put_contents("count/user/$from_id.txt","$co");


file_put_contents("count/user/all.txt","$co1");


if($msrd !=null){
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"$msrd ",
'reply_to_message_id'=>$message_id
]);
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"• تم ارسال رسالتك الى الادمن سيتم الرد عليك في اسرع وقت ✅",
'reply_to_message_id'=>$message_id
]);
}
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"تم ايقاف استقبال الرسائل ",
'reply_to_message_id'=>$message_id
]);
}
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"لاتستيطع استخدام البوت  محظور",
'reply_to_message_id'=>$message_id
]);
}
}}


$photo=$message->photo;
$video=$message->video;
$document=$message->document;
$sticker=$message->sticker;
$voice=$message->voice;
$audio=$message->audio;

$n_id =$msg['1'];
if($reply and $text != 'الغاء الحظر' and $text != 'حظر' and $text != 'معلومات' and $chat_id == $yppee  
and $n_id!= null){
if( in_array($from_id,$sudo)
or in_array($from_id, $adminall)){

if($text){
$get=bot('sendMessage',[
'chat_id'=>$msg['0'],
'text'=>$text,    
'reply_to_message_id'=>$msg['2'],

]);
$msg_id = $get->result->message_id;
}else{

if($photo){
$sens="sendphoto";
$file_id = $update->message->photo[1]->file_id;
}
if($document){
$sens="senddocument";
$file_id = $update->message->document->file_id;
}
if($video){
$sens="sendvideo";
$file_id = $update->message->video->file_id;
}

if($audio){
$sens="sendaudio";
$file_id = $update->message->audio->file_id;
}

if($voice){
$sens="sendvoice";
$file_id = $update->message->voice->file_id;
}

if($sticker){
$sens="sendsticker";
$file_id = $update->message->sticker->file_id;
}

$ss=str_replace("send","",$sens);
$get1=bot($sens,[
"chat_id"=>$msg['0'],
"$ss"=>"$file_id",
'caption'=>"$getfull",
'reply_to_message_id'=>$msg['2'],
]);

$msg_id = $get->result->message_id;
}

$ch_id =$msg['0'];
$name_id =$msg['1'];
$wathqid="$ch_id=$msg_id=$name_id";
file_put_contents("message/$msg_id.txt","$wathqid");

$co_m_ad=file_get_contents("count/admin/$ch_id.txt");
$co=$co_m_ad+1;
file_put_contents("count/admin/$ch_id.txt","$co");

$co_m_all=file_get_contents("count/admin/all.txt");
$coo=$co_m_all+1;
file_put_contents("count/admin/all.txt","$coo");
bot('sendmessage',[
'chat_id'=>$yppee,
'text'=>"
-  تم الارسال بنجاح  [$name_id](tg://user?id=$ch_id) ✉️
",
'reply_to_message_id'=>$message_id
,'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,
'reply_markup'=>json_encode([ 
'inline_keyboard'=>[
[['text'=>" تعديل الرسالة ",'callback_data'=>"edit_msg ".$msg_id]],
[['text'=>" حذف الرسالة ",'callback_data'=>"del_msg ".$msg_id]],
]
])
]);
}}

if (preg_match('/^(del_msg) (.*)/s',$data) ) {
if( in_array($from_id,$sudo)
or in_array($from_id, $adminall)){

  $data1 = explode(" ",$data);
  $wathqid= $data1['1'];
$info=explode("=",file_get_contents("message/$wathqid.txt"));

  $ch_id= $info['0'];
  $msg_id= $info['1'];
  $name_id =$info['2'];
bot('EditMessageText',[
    'chat_id'=>$chat_id,
    'message_id'=>$message_id,
'text'=>"
-  تم حذف رسالة بنجاح 🗑

",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>'رجوع ' ,'callback_data'=>"bot9"]],
]    
])
]);
bot('deleteMessage',[
'chat_id'=>$ch_id,
'message_id'=>$msg_id,
]);
  }
}
if (preg_match('/^(edit_msg) (.*)/s',$data) ) {
if( in_array($from_id,$sudo)
or in_array($from_id, $adminall)){

$data1 = explode(" ",$data);
  $wathqid= $data1['1'];
$info=explode("=",file_get_contents("message/$wathqid.txt"));

  $ch_id= $info['0'];
  $msg_id= $info['1'];
  $name_id =$info['2'];
  file_put_contents("data/t3dil.txt","$ch_id=$msg_id=$name_id");
bot('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"
- قم بارسال رسالتك الجديده ليتم تعديل رسالتك ✉️
",
'reply_to_message_id'=>$message_id
,'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,
 'reply_markup'=>json_encode([ 
      'inline_keyboard'=>[
[['text'=>'رجوع ' ,'callback_data'=>"bot9"]],
]])
]);
file_put_contents("sudo/amr.txt","edit");
  }
}
if($data == "trag3"){
bot('EditMessageText',[
    'chat_id'=>$chat_id,
    'message_id'=>$message_id,
'text'=>'تم الغاء التعديل بنجاح',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>'رجوع ' ,'callback_data'=>"bot9"]],
]    
])
]);
file_put_contents("sudo/amr.txt","");
file_put_contents("data/t3dil.txt","");
}
if($text and $amr == "edit" and $chat_id== $yppee){
if( in_array($from_id,$sudo)
or in_array($from_id, $adminall)){

file_put_contents("sudo/amr.txt","");
$wathqget=file_get_contents("data/t3dil.txt");

  $wathqidd = explode("=",$wathqget);
  $ch_id= $wathqidd['0'];
  $msg_id= $wathqidd['1'];
  $name_id =$wathqidd['2'];
  bot('deleteMessage',[
'chat_id'=>$chat_id,
'message_id'=>$message_id-2,
]);
bot('deleteMessage',[
'chat_id'=>$chat_id,
'message_id'=>$message_id-1,
]);

bot('sendmessage',[
    'chat_id'=>$chat_id,
    'message_id'=>$message_id,
'text'=>"- تم التعديل رساله سابقة للمستخدم  [$name_id](tg://user?id=$ch_id) ✉️",
'reply_to_message_id'=>$message_id
,'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,
'reply_markup'=>json_encode([ 
'inline_keyboard'=>[
[['text'=>" تعديل الرسالة ",'callback_data'=>"edit_msg ".$msg_id],
['text'=>" حذف الرسالة ",'callback_data'=>"del_msg ".$msg_id]],
]
])
]);
file_put_contents("data/t3dil.txt","");
bot('EditMessageText',[
    'chat_id'=>$ch_id,
    'message_id'=>$msg_id,
    'text'=>
$text,
]);
}}

if (preg_match('/^(حظر) (.*)/s',$text) and $chat_id == $yppee ) {
if( in_array($from_id,$sudo)
or in_array($from_id, $adminall)){

$textt = str_replace("حظر ","",$text);
$textt = str_replace(" ","",$text);
$strlen=strlen($textt);
if($strlen < 10){
if(!in_array($textt, $ban)){
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>'تم حظر الشخص من البوت',
'reply_to_message_id'=>$message_id
]);

bot('sendMessage',[
'chat_id'=>$textt,
'text'=>'',
]);
file_put_contents('data/ban.txt', $textt. "\n", FILE_APPEND);
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>'• العضو محظور مسبقآ.!',
'reply_to_message_id'=>$message_id
]);
}
}}
}
if (preg_match('/^(الغاء حظر) (.*)/s',$text) and $chat_id == $yppee ) {
if( in_array($from_id,$sudo)
or in_array($from_id, $adminall)){

$textt = str_replace("الغاء حظر ","",$text);
$textt = str_replace(" ","",$text);
$strlen=strlen($textt);
if($strlen < 10){
if(in_array($textt, $ban)){

bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>' الغاء حظر الشخص من البوت 🚫',
'reply_to_message_id'=>$message_id
]);

bot('sendMessage',[
'chat_id'=>$textt,
'text'=>''
]);
$bin=file_get_contents('data/ban.txt');
$str = str_replace($textt."\n", '' ,$bin);

file_put_contents('data/ban.txt', $str);

}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>' • العضو ليس محظور ❕❕',
'reply_to_message_id'=>$message_id
]);
}}}
}



if($reply and $text == 'حظر' and $chat_id == $yppee  and $n_id!= null){
if( in_array($from_id,$sudo)
or in_array($from_id, $adminall)){

//$from = $message->reply_to_message->forward_from->id;
$from = $msg['0'];
if(!in_array($from, $ban)){
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>'تم حظر الشخص من البوت',
'reply_to_message_id'=>$message_id
]);

bot('sendMessage',[
'chat_id'=>$from,
'text'=>'',
]);

file_put_contents('data/ban.txt', $from. "\n", FILE_APPEND);
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>'• العضو محظور مسبقآ.!',
'reply_to_message_id'=>$message_id
]);
}}
}

if($reply and $text == 'الغاء الحظر' and $chat_id == $yppee and $n_id!= null){
if( in_array($from_id,$sudo)
or in_array($from_id, $adminall)){

//$from = $message->reply_to_message->forward_from->id;
$from = $msg['0'];
if(in_array($from, $ban)){
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>'تم الغاء حظر الشخص من البوت 🚫',
'reply_to_message_id'=>$message_id
]);

bot('sendMessage',[
'chat_id'=>$from,
'text'=>''
]);

$bin=file_get_contents('data/ban.txt');
$str = str_replace($from ."\n", '' ,$bin);

file_put_contents('data/ban.txt', $str);
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>'  • العضو ليس محظور ❕❕',
'reply_to_message_id'=>$message_id,
]);
}
}
}
//معلومات الاعضاء 
if($reply and $text == 'معلومات' and $chat_id == $yppee){
if( in_array($from_id,$sudo)
or in_array($from_id, $adminall)){

//$from = $message->reply_to_message->forward_from->id;
$from = $msg['0'];

$admin = json_decode(file_get_contents("http://api.telegram.org/bot$token/getChat?chat_id=$from"))->result;

$name= $admin->first_name;
$bio = bot('getchat',['chat_id'=>$message->from->id])->result->bio;
$user= $admin->username;

if(!in_array($from, $ban)){

$info="غير محظور";
}else{
$info=" محظور";
}
$co_m_us=file_get_contents("count/user/$from.txt");
$co_m_ad=file_get_contents("count/admin/$from.txt");
$username = $message->from->username;
$photo = "http://telegram.me/$user";
bot('SendPhoto',[
'chat_id'=>$chat_id,
'photo'=>$photo,
'caption'=>"
👤| اسم المستخدم : [ $name](tg://user?id=$from)  .
ℹ️| ايدي المستخدم : $from
📍| معرف المستخدم : *@$user*
🔎| حالة المستخدم : $info
✉️| عدد الرسائل المستلمة منة : $co_m_us 
 📬| عدد الرسائل المرسلة لة : $co_m_ad 
",
'reply_to_message_id'=>$message_id,
'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,
]);
}
}
if( $text == 'معلومات' and !$reply  and $chat_id == $yppee){
if( in_array($from_id,$sudo)
or in_array($from_id, $adminall)){

unlink("sudo/admins.txt");
for($h=0;$h<count($adminall);$h++){
if($adminall[$h] != ""){
$admin = json_decode(file_get_contents("http://api.telegram.org/bot$token/getChat?chat_id=$adminall[$h]"))->result;
$from=$adminall[$h];
$name= $admin->first_name;
$c= $h+1;
$admins="$c - [$name](tg://user?id=$from) `$from`";
file_put_contents("sudo/admins.txt","$admins\n",FILE_APPEND);

}}

$admins=file_get_contents("sudo/admins.txt");


$co_m_us=file_get_contents("count/user/all.txt");
$co_m_ad=file_get_contents("count/admin/all.txt");
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"ℹ معلومات شاملة عن البوت  
~~~~~~~~~~~~~~~~~~~~~~~
👮 - الادمنية : 
$admins
--------------------
👪 - عدد الاعضاء : $cuntei
🚫 - المحضورين : $countben
--------------------
📮 - الرسائل 
📩 - المستلمة :$co_m_us
📬 - الصادرة :$co_m_ad


",
'reply_to_message_id'=>$message_id,
'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,
]);
}
}
$photo=$message->photo;
$video=$message->video;
$document=$message->document;
$sticker=$message->sticker;
$voice=$message->voice;
$audio=$message->audio;
$forward =$message->forward_from_chat;
$c_photo=file_get_contents("data/photo.txt");
$c_video=file_get_contents("data/video.txt");
$c_document=file_get_contents("data/document.txt");
$c_sticker=file_get_contents("data/sticker.txt");
$c_voice=file_get_contents("data/voice.txt");
$c_audio=file_get_contents("data/audio.txt");
$c_forward =file_get_contents("data/audio.txt");
if($from_id!=$admin and $message->chat->type == 'private' ){
//الصور
if($photo and ! $forward){
if($c_photo=="❌"or $c_photo== null){
if($estgbal=="on" or $estgbal==null){

bot('sendMessage',[
'chat_id'=>$yppee,
'text'=>"
",
'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,
'reply_to_message_id'=>$message->reply_to_message->message_id-1,
]);

$get=bot('forwardMessage',[
'chat_id'=>$yppee,
'from_chat_id'=>$chat_id,
'message_id'=>$message_id

]);
$msg_id = $get->result->message_id-1;

$from_id_name="$chat_id=$name=$message_id";
file_put_contents("message/$msg_id.txt","$from_id_name");

$co_m_us=file_get_contents("count/user/$from_id.txt");
$co=$co_m_us+1;
file_put_contents("count/user/$from_id.txt","$co");

file_put_contents("count/user/all.txt","$co1");

if($msrd !=null){
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"$msrd..",
'reply_to_message_id'=>$message_id
]);
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"• تم ارسال رسالتك الى الادمن سيتم الرد عليك في اسرع وقت ✅",
'reply_to_message_id'=>$message_id
]);
}
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"تم ايقاف استقبال الرسائل ",
'reply_to_message_id'=>$message_id
]);
}
}else{

bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"",
'reply_to_message_id'=>$message_id
]);
}

}
//الفيديو
if($video and ! $forward ){
if($c_video=="❌"or $c_photo== null){
if($estgbal=="on" or $estgbal==null){
bot('sendMessage',[
'chat_id'=>$yppee,
'text'=>"
",
'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,
'reply_to_message_id'=>$message->reply_to_message->message_id-1,
]);
$get=bot('forwardMessage',[
'chat_id'=>$yppee,
'from_chat_id'=>$chat_id,
'message_id'=>$message_id

]);
$msg_id = $get->result->message_id-1;

$from_id_name="$chat_id=$name=$message_id";
file_put_contents("message/$msg_id.txt","$from_id_name");

$co_m_us=file_get_contents("count/user/$from_id.txt");
$co=$co_m_us+1;
file_put_contents("count/user/$from_id.txt","$co");
file_put_contents("count/user/all.txt","$co1");


if($msrd !=null){
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"$msrd",
'reply_to_message_id'=>$message_id
]);
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"• تم ارسال رسالتك الى الادمن سيتم الرد عليك في اسرع وقت ✅",
'reply_to_message_id'=>$message_id
]);
}
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"تم ايقاف استقبال الرسائل",
'reply_to_message_id'=>$message_id
]);
}
}else{

bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"",
'reply_to_message_id'=>$message_id
]);
}

}

//الملفات
if($document and ! $forward){
if($c_document=="❌"or $c_photo== null){
if($estgbal=="on" or $estgbal==null){
bot('sendMessage',[
'chat_id'=>$yppee,
'text'=>"
",
'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,
'reply_to_message_id'=>$message->reply_to_message->message_id-1,
]);
$get=bot('forwardMessage',[
'chat_id'=>$yppee,
'from_chat_id'=>$chat_id,
'message_id'=>$message_id

]);
$msg_id = $get->result->message_id-1;

$from_id_name="$chat_id=$name=$message_id";
file_put_contents("message/$msg_id.txt","$from_id_name");

$co_m_us=file_get_contents("count/user/$from_id.txt");
$co=$co_m_us+1;
file_put_contents("count/user/$from_id.txt","$co");
file_put_contents("count/user/all.txt","$co1");

if($msrd !=null){
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"$msrd",
'reply_to_message_id'=>$message_id
]);
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"• تم ارسال رسالتك الى الادمن سيتم الرد عليك في اسرع وقت ✅",
'reply_to_message_id'=>$message_id
]);
}
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"تم ايقاف استقبال ",
'reply_to_message_id'=>$message_id
]);
}
}else{

bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"",
'reply_to_message_id'=>$message_id
]);
}

}

//الملصقات
if($sticker and ! $forward ){
if($c_sticker=="❌"or $c_photo== null){
if($estgbal=="on" or $estgbal==null){
bot('sendMessage',[
'chat_id'=>$yppee,
'text'=>"
",
'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,
'reply_to_message_id'=>$message->reply_to_message->message_id-1,
]);
$get=bot('forwardMessage',[
'chat_id'=>$yppee,
'from_chat_id'=>$chat_id,
'message_id'=>$message_id

]);
$msg_id = $get->result->message_id-1;

$from_id_name="$chat_id=$name=$message_id";
file_put_contents("message/$msg_id.txt","$from_id_name");

$co_m_us=file_get_contents("count/user/$from_id.txt");
$co=$co_m_us+1;
file_put_contents("count/user/$from_id.txt","$co");
file_put_contents("count/user/all.txt","$co1");

if($msrd !=null){
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"$msrd",
'reply_to_message_id'=>$message_id
]);
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"• تم ارسال رسالتك الى الادمن سيتم الرد عليك في اسرع وقت ✅",
'reply_to_message_id'=>$message_id
]);
}
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"تم ايقاف استقبال الرسائل",
'reply_to_message_id'=>$message_id
]);
}
}else{

bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"",
'reply_to_message_id'=>$message_id
]);
}

}

//الصوتيات
if($voice and ! $forward ){
if($c_voice=="❌"or $c_photo== null){
if($estgbal=="on" or $estgbal==null){
bot('sendMessage',[
'chat_id'=>$yppee,
'text'=>"
",
'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,
'reply_to_message_id'=>$message->reply_to_message->message_id-1,
]);
$get=bot('forwardMessage',[
'chat_id'=>$yppee,
'from_chat_id'=>$chat_id,
'message_id'=>$message_id

]);
$msg_id = $get->result->message_id-1;

$from_id_name="$chat_id=$name=$message_id";
file_put_contents("message/$msg_id.txt","$from_id_name");

$co_m_us=file_get_contents("count/user/$from_id.txt");
$co=$co_m_us+1;
file_put_contents("count/user/$from_id.txt","$co");
file_put_contents("count/user/all.txt","$co1");

if($msrd !=null){
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"$msrd",
'reply_to_message_id'=>$message_id
]);
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"• تم ارسال رسالتك الى الادمن سيتم الرد عليك في اسرع وقت ✅",
'reply_to_message_id'=>$message_id
]);
}
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"تم ايقاف استقبال الرسائل ",
'reply_to_message_id'=>$message_id
]);
}
}else{

bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"",
'reply_to_message_id'=>$message_id
]);
}

}
//الصوتيات
if($audio and ! $forward ){
if($c_audio=="❌"or $c_photo== null){
if($estgbal=="on" or $estgbal==null){
bot('sendMessage',[
'chat_id'=>$yppee,
'text'=>"
",
'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,
'reply_to_message_id'=>$message->reply_to_message->message_id-1,
]);
$get=bot('forwardMessage',[
'chat_id'=>$yppee,
'from_chat_id'=>$chat_id,
'message_id'=>$message_id

]);
$msg_id = $get->result->message_id-1;

$from_id_name="$chat_id=$name=$message_id";
file_put_contents("message/$msg_id.txt","$from_id_name");

$co_m_us=file_get_contents("count/user/$from_id.txt");
$co=$co_m_us+1;
file_put_contents("count/user/$from_id.txt","$co");
file_put_contents("count/user/all.txt","$co1");

if($msrd !=null){
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"$msrd",
'reply_to_message_id'=>$message_id
]);
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"• تم ارسال رسالتك الى الادمن سيتم الرد عليك في اسرع وقت ✅",
'reply_to_message_id'=>$message_id
]);
}
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"تم ايقاف استقبال الرسائل ",
'reply_to_message_id'=>$message_id
]);
}
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"",
'reply_to_message_id'=>$message_id
]);
}

}
//التوجية
if($forward ){
if($c_forward=="❌"or $c_forward== null){
if($estgbal=="on" or $estgbal==null){
bot('sendMessage',[
'chat_id'=>$yppee,
'text'=>"
",
'parse_mode'=>"MarkDown",
'disable_web_page_preview'=>true,
'reply_to_message_id'=>$message->reply_to_message->message_id-1,
]);
$get=bot('forwardMessage',[
'chat_id'=>$yppee,
'from_chat_id'=>$chat_id,
'message_id'=>$message_id

]);
$msg_id = $get->result->message_id-1;

$from_id_name="$chat_id=$name=$message_id";
file_put_contents("message/$msg_id.txt","$from_id_name");

$co_m_us=file_get_contents("count/user/$from_id.txt");
$co=$co_m_us+1;
file_put_contents("count/user/$from_id.txt","$co");
file_put_contents("count/user/all.txt","$co1");

if($msrd !=null){
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"$msrd",
'reply_to_message_id'=>$message_id
]);
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"• تم ارسال رسالتك الى الادمن سيتم الرد عليك في اسرع وقت ✅",
'reply_to_message_id'=>$message_id
]);
}
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"تم ايقاف استقبال الرسائل",
'reply_to_message_id'=>$message_id
]);
}
}else{
bot('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"",
'reply_to_message_id'=>$message_id
]);
}

}
}


if(strstr($text,"t.me") == true or strstr($text,"telegram.me") == true or strstr($text,"https://") == true or strstr($text,"://") == true or strstr($text,"wWw.") == true or strstr($text,"WwW.") == true or strstr($text,"T.me/") == true or strstr($text,"WWW.") == true or strstr($caption,"t.me") == true or strstr($caption,"telegram.me")) {   
if($users == "مقفول"){
	    bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>" يمنع ارسال الروابط .",
        ]);
}
}


$c_photo=file_get_contents("data/photo.txt");
$c_video=file_get_contents("data/video.txt");
$c_document=file_get_contents("data/document.txt");
$c_sticker=file_get_contents("data/sticker.txt");
$c_voice=file_get_contents("data/voice.txt");
$c_audio=file_get_contents("data/audio.txt");
$c_forward =file_get_contents("data/audio.txt");

if($text=="قفل الصور" and in_array($from_id,$sudo)){
file_put_contents("data/photo.txt","✅");
bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>"- تم قفل الصور بنجاح✅،",
        ]);
}

if($text=="فتح الصور" and in_array($from_id,$sudo)){
file_put_contents("data/photo.txt","❌");
bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>"- تم فتح الصور بنجاح✅،",
        ]);
}
if($text=="قفل الفيديو" and in_array($from_id,$sudo)){
file_put_contents("data/video.txt","✅");

bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>"- تم قفل الفيديو بنجاح✅، ",
        ]);
}
if($text=="فتح الفيديو" and in_array($from_id,$sudo)){
file_put_contents("data/video.txt","❌");
bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>"- تم فتح الفيديو بنجاح✅،",
        ]);
}

if($text=="قفل الملفات" and in_array($from_id,$sudo)){
file_put_contents("data/document.txt","✅");

bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>" تم  $text ✅",
        ]);
}
if($text=="فتح الملفات" and in_array($from_id,$sudo)){
file_put_contents("data/document.txt","❌");
bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>" تم  $text ✅",
        ]);
}

if($text=="قفل الملصقات" and in_array($from_id,$sudo)){
file_put_contents("data/sticker.txt","✅");

bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>" تم  $text ✅",
        ]);
}
if($text=="فتح الملصقات" and in_array($from_id,$sudo)){
file_put_contents("data/sticker.txt","❌");
bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>" تم  $text ✅",
        ]);
}

if($text=="قفل الصوت" and in_array($from_id,$sudo)){
file_put_contents("data/voice.txt","✅");

bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>" تم  $text ✅",
        ]);
}
if($text=="فتح الصوت" and in_array($from_id,$sudo)){
file_put_contents("data/voice.txt","❌");
bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>" تم  $text ✅",
        ]);
}


if($text=="قفل الميوزك" and in_array($from_id,$sudo)){
file_put_contents("data/audio.txt","✅");

bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>" تم  $text ✅",
        ]);
}
if($text=="فتح الميوزك" and in_array($from_id,$sudo)){
file_put_contents("data/audio.txt","❌");
bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>" تم  $text ✅",
        ]);
}
if($text=="قفل التوجيه" and in_array($from_id,$sudo)){
file_put_contents("data/forward.txt","✅");
bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>" تم  $text ✅",
        ]);
}
if($text=="فتح التوجيه" and in_array($from_id,$sudo)){
file_put_contents("data/forward.txt","❌");
bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>" تم  $text ✅",
        ]);
}

if($text=="قفل الكل" and in_array($from_id,$sudo)){
file_put_contents("data/forward.txt","✅");
file_put_contents("data/audio.txt","✅");
file_put_contents("data/voice.txt","✅");
file_put_contents("data/sticker.txt","✅");
file_put_contents("data/document.txt","✅");
file_put_contents("data/video.txt","✅");
file_put_contents("data/photo.txt","✅");
bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>" تم  $text ✅",
        ]);
}
if($text=="فتح الكل" and in_array($from_id,$sudo)){
file_put_contents("data/forward.txt","❌");
file_put_contents("data/audio.txt","❌");
file_put_contents("data/voice.txt","❌");
file_put_contents("data/sticker.txt","❌");
file_put_contents("data/document.txt","❌");
file_put_contents("data/video.txt","❌");
file_put_contents("data/photo.txt","❌");
bot('sendmessage',[
       'chat_id'=>$chat_id,
        'text'=>" تم  $text ✅",
        ]);
}


$c_photo=file_get_contents("data/photo.txt");
$c_video=file_get_contents("data/video.txt");
$c_document=file_get_contents("data/document.txt");
$c_sticker=file_get_contents("data/sticker.txt");
$c_voice=file_get_contents("data/voice.txt");
$c_audio=file_get_contents("data/audio.txt");
$c_forward =file_get_contents("data/audio.txt");
