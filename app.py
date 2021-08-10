import glob
import time

from imutils.paths import list_images
import streamlit as st
import utils
import cv2
import os


class App:

    def __init__(self):
        self.name_app = 'Dataset Process'
        self.pages = ('Classes', 'Imagens', 'Anotadas')
        self.groups = ['acaro', 'bicudo', 'lagarta', 'mosca', 'percevejo']
        self.phases = ['ovo', 'ovo_eclodindo', 'larva', 'adulto']
        self.error_file = 'Nenhum arquivo foi encontrado.'
        self.success = 'Arquivos renomeados com sucesso.'

    def sidebar_menu(self):

        my_sidebar = st.sidebar
        my_sidebar.image('astronauta.png', width=128)

        my_sidebar.title(self.name_app)
        my_sidebar.markdown('Aplicação para renomear novos arquivos do dataset.')

        page = my_sidebar.radio('Renomear:', self.pages)
        if page == self.pages[0]:
            self.classes()
        elif page == self.pages[1]:
            self.rename_images()
        elif page == self.pages[2]:
            self.rename_all_files()

    @staticmethod
    def classes():

        st.title('Classes:')
        names = utils.open_file('flags.json')
        classes = []
        for i, n in enumerate(names['flags']):
            if i == 0:
                pass
            else:
                classes.append(n.split('__')[1])
        st.write('Nosso conjunto de dados contém as seguintes classes:')

        classes = sorted(list(set(classes)))

        c = st.selectbox('Classes: ', classes)
        st.write('Copie o nome abaixo:')
        st.code(c)

    def rename_images(self):
        with st.form('rename-images'):
            st.title('Renomear imagens')
            st.write('Indique o caminho das imagens que deseja renomear e configure os parâmetros abaixo:')
            path_file = st.text_input('Caminho:')
            group = st.selectbox('Grupo:', self.groups)
            specie = st.text_input('Nome científico:', )
            phase = st.selectbox('Fase:', self.phases)
            start = st.number_input('Índice inicial:')
            button = st.form_submit_button('Renomear')

            start = int(start)

            if button:
                data = {
                    'path': path_file,
                    'group': group,
                    'specie': specie,
                    'phase': phase,
                    'start': start
                }

                images = list(list_images(path_file))

                if len(images) > 0:
                    st.markdown(f'Foram encontradas **{len(images)}** imagens.')
                    st.code('Renomenado imagens ...')

                    for image in images:
                        new_name = f"{group}__{specie}__{phase}__{start:05}.jpg"
                        frame = cv2.imread(image)

                        cv2.imwrite(f'./images/{new_name}', frame)

                        start += 1

                    st.info(self.success)

                    st.markdown('**OBS:** As imagens foram salvas na pasta ***images***')
                else:
                    st.warning(self.error_file)

                st.write(data)

    def rename_all_files(self):

        with st.form('rename-all-files'):
            st.title('Renomear anotações')
            st.write('Indique o caminho dos arquivos que deseja renomear e configure os parâmetros abaixo:')
            path_file = st.text_input('Caminho:')
            group = st.selectbox('Grupo:', self.groups)
            specie = st.text_input('Nome científico:', )
            phase = st.selectbox('Fase:', self.phases)
            start = st.number_input('Índice inicial:')
            button = st.form_submit_button('Renomear')

            start = int(start)

            if button:
                data = {
                    'path': path_file,
                    'group': group,
                    'specie': specie,
                    'phase': phase,
                    'start': start
                }

                annotations = glob.glob(f'{path_file}/*.json')

                flags = utils.open_file(os.path.join('./', 'flags.json'))

                if len(annotations) > 0:
                    st.write(f'Foram encontradas **{len(annotations)}** anotações')
                    st.code('Renomeando arquivos...')
                    for a in annotations:
                        new_name = f'{group}__{specie}__{phase}__{start:05}'
                        old_name = os.path.splitext(a)[0]

                        print(old_name)
                        print(new_name)

                        # rename image and json
                        utils.rename(path_file, old_name, new_name, 'jpg', ['jpg', 'jpeg'])
                        utils.rename(path_file, old_name, new_name, 'json', ['json'])

                        # rename label json and image path
                        json_path = os.path.join(path_file, f'{new_name}.json')
                        temp_json = utils.open_file(json_path)

                        for shape in range(len(temp_json['shapes'])):
                            temp_json['shapes'][shape]['label'] = f'{group}__{specie}__{phase}'

                        temp_json['flags'] = flags['flags']
                        temp_json['imagePath'] = f'{new_name}.jpg'
                        utils.save_json(json_path, temp_json)

                        start += 1

                    st.info(self.success)

                else:
                    st.warning(self.error_file)

                st.write(data)

    def run(self):
        self.sidebar_menu()


if __name__ == '__main__':
    app = App()
    app.run()
