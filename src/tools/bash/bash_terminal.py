import os
import asyncio


class BashTerminal:

    def __init__(
        self,
        cwd: str = None,
        delimiter: str = f"<terminal-command-exit-{os.urandom(4).hex()}>",
        output_delay: float = 0.2,
        output_timeout: int = 120,
    ):
        self._cwd = cwd
        self._delimiter = delimiter
        self._output_delay = output_delay
        self._output_timeout = output_timeout
        self._process: asyncio.subprocess.Process = None

    def _get_bash_shell_process(self):
        return asyncio.create_subprocess_exec(
            "/bin/bash",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self._cwd,
            preexec_fn=os.setsid,
        )

    def _get_powershell_process(self):
        return asyncio.create_subprocess_exec(
            "powershell.exe",
            "-NoLogo",
            "-NoProfile",
            "-NoExit",
            "-Command",
            "-",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self._cwd,
        )

    async def start(self):
        if self._process:
            return

        if os.name != "nt":
            self._process = await self._get_bash_shell_process()
        else:
            self._process = await self._get_powershell_process()

    async def stop(self):
        if not self._process:
            return

        try:
            self._process.terminate()
            await asyncio.wait_for(self._process.communicate(), timeout=5.0)
        except asyncio.TimeoutError:
            try:
                self._process.kill()
                await asyncio.wait_for(self._process.communicate(), timeout=5.0)
            except asyncio.TimeoutError:
                pass
        finally:
            self._process = None

    def _get_command(self, cmd: str):
        cmd = cmd.strip()
        if not cmd.endswith(";"):
            cmd += ";"
        cmd += f" echo '{self._delimiter}'\n"
        return cmd

    def _decode_buffer(self, buffer: bytes):
        try:
            return buffer.decode("utf-8")
        except Exception:
            return buffer.decode("utf-8", errors="replace")

    async def run(self, cmd: str):
        if not self._process:
            await self.start()

        output = ""
        stderr = ""

        self._process.stdin.write(self._get_command(cmd).encode("utf-8"))
        await self._process.stdin.drain()

        try:
            async with asyncio.timeout(self._output_timeout):

                while True:
                    await asyncio.sleep(self._output_delay)

                    output += self._decode_buffer(self._process.stdout._buffer)
                    stderr += self._decode_buffer(self._process.stderr._buffer)

                    if stderr:
                        break

                    if self._delimiter in output:
                        output = output[: output.index(self._delimiter)]
                        break

        except Exception as e:
            if not stderr:
                stderr = f"{e}"

        self._process.stdout._buffer.clear()
        self._process.stderr._buffer.clear()

        return str(
            {
                "command": cmd,
                "stdout": output,
                "stderr": stderr,
            }
        )


if __name__ == "__main__":

    async def main():
        terminal = BashTerminal()
        try:
            res = await terminal.run("ls")
            print(res)
        finally:
            await terminal.stop()

    asyncio.run(main())
