import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    message: "これはVercel上のPythonから返信しています！",
    status: "success"
  });
}