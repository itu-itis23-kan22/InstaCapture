from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

# Import the story downloader logic
from instastalk import InstaStalker

class StoryDownloaderApp(App):
    def build(self):
        self.stalker = InstaStalker()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Instagram Story Downloader', size_hint=(1, 0.2)))
        self.username_input = TextInput(hint_text='Enter Instagram username', size_hint=(1, 0.2))
        layout.add_widget(self.username_input)
        download_button = Button(text='Download Stories', size_hint=(1, 0.2))
        download_button.bind(on_press=self.on_download)
        layout.add_widget(download_button)
        self.status_label = Label(text='', size_hint=(1, 0.4))
        layout.add_widget(self.status_label)
        return layout

    def on_download(self, instance):
        username = self.username_input.text.strip()
        if not username:
            self.status_label.text = 'Please enter a username.'
            return
        self.status_label.text = f'Downloading stories for {username}...'
        success = self.stalker.download_story(username)
        if success:
            self.status_label.text = f'Stories for {username} downloaded successfully.'
        else:
            self.status_label.text = f'Failed to download stories for {username}.'

if __name__ == '__main__':
    StoryDownloaderApp().run() 