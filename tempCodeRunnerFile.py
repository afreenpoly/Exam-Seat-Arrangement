flash('Upload successful', 'success')
        return render_template('timetableupload.html')
    else:
        flash('Upload failed', 'danger')
        return render_template('timetableupload.html')