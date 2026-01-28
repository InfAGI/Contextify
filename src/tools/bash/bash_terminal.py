import os
import asyncio
from src.utils.log import logger


class BashTerminal:

    def __init__(
        self,
        cwd: str = None,
        delimiter: str = "<terminal-command-exit>",
        output_delay: float = 0.2,
        output_timeout: int = 120,
    ):
        self._cwd = cwd
        self._delimiter = delimiter
        self._output_delay = output_delay
        self._output_timeout = output_timeout
        self._process: asyncio.subprocess.Process = None

    async def start(self):
        if self._process:
            return

        if os.name != "nt":
            self._process = await asyncio.create_subprocess_exec(
                "/bin/bash",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self._cwd,
                preexec_fn=os.setsid,
            )
        else:
            self._process = await asyncio.create_subprocess_exec(
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

            init_cmd = "$OutputEncoding = [Console]::InputEncoding = [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding;"
            self._process.stdin.write((init_cmd + "\n").encode("utf-8"))
            await self._process.stdin.drain()
            try:
                self._process.stdout._buffer.clear()
                self._process.stderr._buffer.clear()
            except Exception:
                pass

    async def stop(self):
        if not self._process:
            return

        try:
            if self._process.stdin:
                self._process.stdin.close()
            self._process.terminate()
            await self._process.wait()
            logger.info("Bash terminal terminated successfully.")
        except asyncio.TimeoutError:
            logger.error("Bash terminal termination timed out.")
            try:
                self._process.kill()
                await self._process.wait()
                logger.info("Bash terminal killed successfully.")
            except asyncio.TimeoutError:
                logger.error("Bash terminal kill timed out.")
                pass
        finally:
            self._process = None
            # logger.info("Bash terminal process cleaned up.")

    def get_command(self, cmd: str):
        # logger.info(f"Executing command before: {cmd}")
        cmd = cmd.strip()
        if not cmd.endswith(";"):
            cmd += ";"
        cmd += f" echo '{self._delimiter}'\n"
        # logger.info(f"Executing command after: {cmd.strip()}")
        return cmd

    async def run(self, cmd: str):
        if not self._process:
            await self.start()

        self._process.stdin.write(self.get_command(cmd).encode("utf-8"))
        await self._process.stdin.drain()

        try:
            async with asyncio.timeout(self._output_timeout):

                while True:
                    await asyncio.sleep(self._output_delay)

                    output = self._process.stdout._buffer.decode()

                    stderr = self._process.stderr._buffer.decode()
                    if stderr:
                        break

                    if self._delimiter in output:
                        output = output[: output.index(self._delimiter)]
                        break

        except Exception as e:
            logger.error(f"Execute command: {cmd} with error: {e}")
            pass

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
        # terminal = PowerShellTerminal(cwd=initial_dir)
        try:
            # res = await terminal.run("pwd")
            # print(res)
            # res = await terminal.run("ls")
            # print(res)
            # res = await terminal.run("cd ..")
            # print(res)
            res = await terminal.run("pwd && ls -la")
            print(res)
        finally:
            await terminal.stop()
            # pass

    asyncio.run(main())

    print("--- Test Completed ---")
