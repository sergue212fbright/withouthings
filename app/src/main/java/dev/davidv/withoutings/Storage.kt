package dev.davidv.withoutings

import android.content.Context
/** Health history and its SQLite journal stay inside Android's app sandbox. */
fun watchDb(context: Context): String {
    val database = context.getDatabasePath("watch.db")
    val directory = checkNotNull(database.parentFile)
    check(directory.isDirectory || directory.mkdirs()) { "Cannot create private health storage" }
    return database.absolutePath
}
