package dev.davidv.withoutings.net

import java.io.ByteArrayOutputStream
import java.io.IOException
import java.io.InputStream
import java.net.URI

internal const val MAX_TILE_BYTES = 1024 * 1024

/** Custom providers receive route areas, so only explicit HTTPS URLs are accepted. */
fun isSafeTileTemplate(template: String): Boolean {
    if (!listOf("{z}", "{x}", "{y}").all(template::contains)) return false
    val expanded = template.replace("{z}", "0").replace("{x}", "0").replace("{y}", "0")
    val uri = runCatching { URI(expanded) }.getOrNull() ?: return false
    return uri.scheme.equals("https", ignoreCase = true) &&
        !uri.host.isNullOrBlank() && uri.userInfo == null && uri.fragment == null &&
        (uri.port == -1 || uri.port in 1..65535)
}

/** Content-Length is optional and untrusted; enforce the limit while reading too. */
internal fun readTileBytes(input: InputStream): ByteArray {
    val output = ByteArrayOutputStream()
    val buffer = ByteArray(8192)
    while (true) {
        val count = input.read(buffer)
        if (count == -1) return output.toByteArray()
        if (output.size() + count > MAX_TILE_BYTES) throw IOException("Map tile is too large")
        output.write(buffer, 0, count)
    }
}
