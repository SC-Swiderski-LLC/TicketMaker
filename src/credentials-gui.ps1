Add-Type -AssemblyName System.Windows.Forms

# Define credential names
$urlCredentialName = "TicketMaker_FreshdeskURL"
$apiKeyCredentialName = "TicketMaker_APIKey"

# Create the form
$form = New-Object System.Windows.Forms.Form
$form.Text = "TicketMaker Configuration"
$form.Size = New-Object System.Drawing.Size(400, 200)
$form.StartPosition = "CenterScreen"

# Add a label and textbox for the URL
$labelUrl = New-Object System.Windows.Forms.Label
$labelUrl.Text = "Freshdesk URL:"
$labelUrl.Location = New-Object System.Drawing.Point(10, 20)
$labelUrl.Size = New-Object System.Drawing.Size(100, 20)
$form.Controls.Add($labelUrl)

$textboxUrl = New-Object System.Windows.Forms.TextBox
$textboxUrl.Location = New-Object System.Drawing.Point(120, 20)
$textboxUrl.Size = New-Object System.Drawing.Size(250, 20)
$form.Controls.Add($textboxUrl)

# Add a label and textbox for the API Key
$labelApiKey = New-Object System.Windows.Forms.Label
$labelApiKey.Text = "API Key:"
$labelApiKey.Location = New-Object System.Drawing.Point(10, 60)
$labelApiKey.Size = New-Object System.Drawing.Size(100, 20)
$form.Controls.Add($labelApiKey)

$textboxApiKey = New-Object System.Windows.Forms.TextBox
$textboxApiKey.Location = New-Object System.Drawing.Point(120, 60)
$textboxApiKey.Size = New-Object System.Drawing.Size(250, 20)
$form.Controls.Add($textboxApiKey)

# Add OK button
$okButton = New-Object System.Windows.Forms.Button
$okButton.Text = "OK"
$okButton.Location = New-Object System.Drawing.Point(150, 120)
$okButton.Add_Click({
    if ($textboxUrl.Text -and $textboxApiKey.Text) {
        # Store credentials in Credential Manager
        cmdkey /generic:$urlCredentialName /user:"URL" /pass:$($textboxUrl.Text)
        cmdkey /generic:$apiKeyCredentialName /user:"APIKey" /pass:$($textboxApiKey.Text)
        [System.Windows.Forms.MessageBox]::Show("Credentials stored successfully!")
        $form.Close()
    } else {
        [System.Windows.Forms.MessageBox]::Show("Please fill out both fields.")
    }
})
$form.Controls.Add($okButton)

# Show the form
$form.ShowDialog()
