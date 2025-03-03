plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}


android {
    namespace = "com.example.robotcontroller"
    compileSdk = 33

    defaultConfig {
        applicationId = "com.example.robotcontroller"
        minSdk = 21
        targetSdk = 33
        versionCode = 1
        versionName = "1.0"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        viewBinding = true
    }

    java {
        toolchain {
            languageVersion.set(JavaLanguageVersion.of(21)) // Use Java 17
        }
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.10.1")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.8.0")
    implementation("com.squareup.okhttp3:okhttp:4.9.3")

    // JUnit for unit testing
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
}
