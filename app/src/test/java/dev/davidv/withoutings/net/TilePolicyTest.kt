package dev.davidv.withoutings.net

import java.io.ByteArrayInputStream
import java.io.IOException
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class TilePolicyTest {
    @Test fun `HTTPS providers and query tokens are accepted`() {
        assertTrue(isSafeTileTemplate("https://tile.openstreetmap.org/{z}/{x}/{y}.png"))
        assertTrue(isSafeTileTemplate("https://maps.example:8443/{z}/{x}/{y}?key=user-provided"))
    }

    @Test fun `insecure URLs embedded credentials and incomplete templates are rejected`() {
        listOf(
            "http://maps.example/{z}/{x}/{y}",
            "file:///tmp/{z}/{x}/{y}",
            "https://user:password@maps.example/{z}/{x}/{y}",
            "https://maps.example/{z}/{x}",
            "https://maps.example/{z}/{x}/{y}#fragment",
            "https://maps.example:0/{z}/{x}/{y}",
            "https:///{z}/{x}/{y}",
        ).forEach { assertFalse(it, isSafeTileTemplate(it)) }
    }

    @Test fun `a complete tile is preserved`() {
        val bytes = ByteArray(MAX_TILE_BYTES) { (it % 251).toByte() }
        assertArrayEquals(bytes, readTileBytes(ByteArrayInputStream(bytes)))
    }

    @Test(expected = IOException::class)
    fun `an oversized response is rejected without trusting content length`() {
        readTileBytes(ByteArrayInputStream(ByteArray(MAX_TILE_BYTES + 1)))
    }
}
