plugins {
    kotlin("jvm") version "1.9.24"
    application
}

group = "dev.carvalhocaio"
version = "0.1.0"

repositories {
    mavenCentral()
}

kotlin {
    jvmToolchain(21)
}

application {
    // MainKt = main() function in app/src/main/kotlin/githubactivity/Main.kt
    mainClass.set("githubactivity.MainKt")
}
