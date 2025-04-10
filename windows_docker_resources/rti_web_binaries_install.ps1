 if ( $Env:ROS_DISTRO -eq "jammy" -or $Env:ROS_DISTRO -eq "humble" ) {
	pixi run 7z x -oC:\connext "C:\TEMP\rticonnextdds-src\openssl-1.1.1k-target-x64Win64VS2017.zip"
	& "C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-host-x64Win64.exe" @(--mode unattended --unattendedmodeui minimalWithDialogs --prefix "C:\connext")
	& $Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat -u "C:\TEMP\rticonnextdds-src\openssl-1.1.1k-6.0.1.25-host-x64Win64.rtipkg"
	& $Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat -u "C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-target-x64Win64VS2017.rtipkg"
	& $Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat -u "C:\TEMP\rticonnextdds-src\rti_security_plugins-6.0.1.25-host-x64Win64.rtipkg"
	& $Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat -u "C:\TEMP\rticonnextdds-src\rti_security_plugins-6.0.1.25-target-x64Win64VS2017.rtipkg"
} else {
	"C:\TEMP\rticonnextdds-src\rti_connext_dds-7.3.0-pro-host-x64Win64.exe" @(--mode unattended --unattendedmodeui minimalWithDialogs --prefix "C:\connext")
	& $Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat -u "C:\TEMP\rticonnextdds-src\openssl-3.0.12-7.3.0-host-x64Win64.rtipkg"
	& $Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat -u "C:\TEMP\rticonnextdds-src\openssl-3.0.12-7.3.0-target-x64Win64VS2017.rtipkg"
	& $Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat -u "C:\TEMP\rticonnextdds-src\rti_connext_dds-7.3.0-pro-target-x64Win64VS2017.rtipkg"
	& $Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat -u "C:\TEMP\rticonnextdds-src\rti_security_plugins-7.3.0-host-x64Win64.rtipkg"
	& $Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat -u "C:\TEMP\rticonnextdds-src\rti_security_plugins-7.3.0-target-x64Win64VS2017.rtipkg"
}
