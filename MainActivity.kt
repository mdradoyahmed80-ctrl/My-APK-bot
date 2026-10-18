package com.example.personalagent

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) { super.onCreate(savedInstanceState); setContent { AgentHome() } }
}

@Composable fun AgentHome() {
    var message by remember { mutableStateOf("") }
    var log by remember { mutableStateOf(listOf("স্বাগতম! এটি Personal AI Agent-এর Android companion starter." , "এখনো backend-এ যুক্ত হয়নি; এখানে কোনো ফোন অ্যাকশন চালানো হয় না.")) }
    MaterialTheme {
        Scaffold(topBar = { TopAppBar(title = { Text("Personal AI Agent") }) }) { padding ->
            Column(Modifier.fillMaxSize().padding(padding).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("দোস্ত, এখানে তোমার chat ও task dashboard তৈরি হবে।", style = MaterialTheme.typography.titleMedium)
                LazyColumn(Modifier.weight(1f).fillMaxWidth()) { items(log) { Text(it, Modifier.fillMaxWidth().padding(vertical=5.dp)) } }
                OutlinedTextField(value=message,onValueChange={message=it},label={Text("কী করতে চাও লিখো")},modifier=Modifier.fillMaxWidth())
                Button(onClick={ if(message.isNotBlank()) { log=log + "তোমার অনুরোধ: $message" + " (ডেমো—এখনো পাঠানো হয়নি)"; message="" } },modifier=Modifier.fillMaxWidth()) { Text("Send demo message") }
                Text("নিরাপত্তা: microphone / accessibility / অন্য অ্যাপের নিয়ন্ত্রণ স্বয়ংক্রিয়ভাবে চালু করা হয়নি।")
            }
        }
    }
}
